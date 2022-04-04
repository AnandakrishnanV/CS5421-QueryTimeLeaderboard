import os
import uuid
import jwt
from datetime import datetime, timezone, timedelta
from celery.utils.log import get_task_logger

from flask import Flask, request, jsonify, session, make_response
from flask_restful import reqparse, Resource, Api, abort
from psycopg2 import Error
from celery import Celery
from db_client import get_db_connection, execute_query, validate_sql_syntax
from util import RetryableError, BenchMarkTask, process_error, NonRetryableError
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# create readonly user or grant only select permission for executing benchmarking queries to avoid injection
# write permission is given to admin users like the professor or TAs

app = Flask(__name__)
api = Api(app)
logger = get_task_logger(__name__)

app.config['celery_broker_url'] = os.environ.get("REDIS_URL")
app.config['celery_result_backend'] = os.environ.get("REDIS_URL")

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['APP_DB_HOST'] = os.environ.get("APP_DB_HOST")
app.config['APP_DB_PORT'] = os.environ.get("APP_DB_PORT")
app.config['APP_DB_NAME'] = os.environ.get("APP_DB_NAME")
app.config['APP_DB_USER'] = os.environ.get("APP_DB_USER")
app.config['APP_DB_PASSWORD'] = os.environ.get("APP_DB_PASSWORD")
app.config['BENCHMARK_DB_HOST'] = os.environ.get("BENCHMARK_DB_HOST")
app.config['BENCHMARK_DB_PORT'] = os.environ.get("BENCHMARK_DB_PORT")
app.config['BENCHMARK_DB_USER'] = os.environ.get("BENCHMARK_DB_USER")
app.config['BENCHMARK_DB_PASSWORD'] = os.environ.get("BENCHMARK_DB_PASSWORD")
app.config['BENCHMARK_DB_NAME'] = os.environ.get("BENCHMARK_DB_NAME")
app.config['BENCHMARK_TIMEOUT'] = os.environ.get("BENCHMARK_TIMEOUT")
app.config['JWT_CONFIG'] = os.environ.get("JWT_CONFIG")  # POST_ONLY OR ALL

CHALLENGE_TYPE_SLOWEST_QUERY = 1

celery = Celery(app.name, broker=app.config['celery_broker_url'], backend=app.config['celery_result_backend'])
celery.conf.update(app.config)

challenge_parser = reqparse.RequestParser()
challenge_parser.add_argument('user_name', type=str, required=True, help="User name cannot be blank!")
challenge_parser.add_argument('query', type=str, required=True, help="Query cannot be blank!")
challenge_parser.add_argument('challenge_name', type=str, required=True, help="Challenge name cannot be blank!")
challenge_parser.add_argument('challenge_type', type=int, required=True, help="Challenge type cannot be blank!")
challenge_parser.add_argument('challenge_description', type=str, required=True,
                              help="Challenge description cannot be blank!")

submission_parser = reqparse.RequestParser()
submission_parser.add_argument('query', type=str, required=True, help="Query cannot be blank!")
submission_parser.add_argument('user_name', type=str, required=True, help="User name cannot be blank!")
submission_parser.add_argument('challenge_id', type=str, required=True, help="Challenge ID cannot be blank!")

submission_list_parser = reqparse.RequestParser()
submission_list_parser.add_argument('user_name', type=str)
submission_list_parser.add_argument('challenge_id', type=str)
challenge_list_parser = reqparse.RequestParser()
challenge_list_parser.add_argument('user_name', type=str)

challenge_type_parser = reqparse.RequestParser()
challenge_type_parser.add_argument('user_name', type=str, required=True, help="User name cannot be blank!")
challenge_type_parser.add_argument('description', type=str, required=True, help="Description cannot be blank!")
challenge_type_parser.add_argument('challenge_type', type=str, required=True, help="Challenge type cannot be blank!")

login_parser = reqparse.RequestParser()
login_parser.add_argument('user_name', type=str, required=True, help="User name cannot be blank!")
login_parser.add_argument('password', type=str, required=True, help="Password cannot be blank!")

DIFF_QUERY_TEMPLATE = '''SELECT CASE WHEN COUNT(*) = 0 THEN 'Same' ELSE 'Different' END FROM (({} EXCEPT {}) UNION ({} EXCEPT {})) AS RESULT'''


def token_required(func):
    # decorator factory which invokes update_wrapper() method and passes decorated function as an argument
    @wraps(func)
    def decorated(*args, **kwargs):
        if app.config['JWT_CONFIG'] == 'POST_ONLY' and request.method == 'GET':
            return func(*args, **kwargs)
        token = request.headers.get('token')
        user_name = request.headers.get('user')
        if not token:
            return make_response(jsonify({'Alert!': 'Token is missing in request header!'}), 401)
        elif not user_name:
            return make_response(jsonify({'Alert!': 'User name is missing in request header!'}), 401)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            if not data.get("user_name") or user_name != data.get("user_name"):
                return make_response(jsonify({'Message': 'Invalid token'}), 403)
        except:
            return make_response(jsonify({'Message': 'Invalid token'}), 403)
        return func(*args, **kwargs)

    return decorated


def check_admin(user_name: str):
    admin_query = 'SELECT is_admin FROM users WHERE user_name = %s'
    conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                             user=app.config.get('APP_DB_USER'), password=app.config.get('APP_DB_PASSWORD'),
                             port=app.config.get('APP_DB_PORT'))
    cur = execute_query(db_conn=conn, query=admin_query, values=(user_name,))
    is_admin = cur.fetchone()
    cur.close()
    conn.close()
    return False if not is_admin else is_admin[0]


class Login(Resource):
    def post(self):

        args = login_parser.parse_args()
        user_name = args['user_name']
        password = args['password']
        # to generate the hashed password, use generate_password_hash(<password str>, method='sha256')

        try:
            conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config['APP_DB_NAME'],
                                     user=app.config.get('APP_DB_USER'), password=app.config.get('APP_DB_PASSWORD'),
                                     port=app.config.get('APP_DB_PORT'),
                                     readonly=True)
            cur = execute_query(db_conn=conn, query='SELECT * FROM users WHERE user_name = %s ',
                                values=(user_name,))

            current_user = cur.fetchone()
            hashed_password = current_user['password']
            cur.close()
            conn.close()

            if current_user and check_password_hash(hashed_password, password):
                session['logged_in'] = True

                token = jwt.encode({
                    'user_name': user_name,
                    'exp': datetime.utcnow() + timedelta(minutes=30)
                },
                    app.config['SECRET_KEY'])
                return make_response(jsonify({'token': token, 'is_admin': current_user['is_admin']}), 200)
            else:
                return make_response(jsonify({'message': 'Authentication Failed'}), 403)
        except (Exception, Error) as error:
            print(f'Login check failed, error: {error}')
            return abort(500, message="Internal Server Error")


@celery.task(throws=(RetryableError, NonRetryableError), autoretry_for=(RetryableError,), retry_backoff=True,
             max_retries=10, base=BenchMarkTask)
def benchmark_query(baseline_query: str, query: str, submission_id):
    try:
        conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                 user='read_user',
                                 password='read_user',
                                 port=app.config.get('BENCHMARK_DB_PORT'),
                                 timeout=app.config.get('BENCHMARK_TIMEOUT'), readonly=True)
        cur = execute_query(db_conn=conn, query=f"EXPLAIN ANALYZE {query}")
        explain_result = cur.fetchall()
        logger.info(f'Benchmark result, {explain_result[-2][0]}, {explain_result[-1][0]}')
        cur.close()
        conn.close()
    except (Exception, Error) as error:
        logger.warning(f'Benchmark query failed, error: {error}')
        if 'canceling statement due to statement timeout' in str(error):
            logger.warning(
                f'Benchmark result maximum total time {app.config.get("BENCHMARK_TIMEOUT")}ms for planning and execution reached')
            # still update on timeout
            try:
                dt = datetime.now(timezone.utc)
                conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                         user=app.config.get('APP_DB_USER'),
                                         port=app.config.get('APP_DB_PORT'),
                                         password=app.config.get('APP_DB_PASSWORD'))
                cur = execute_query(db_conn=conn,
                                    query="UPDATE submission SET updated_at = %s, error_message = 'query timeout' WHERE submission_id = %s",
                                    values=(dt, submission_id))
                count = cur.rowcount
                cur.close()
                conn.close()
                logger.info(f"{count} records successfully updated for submission table on benchmarking timeout")
            except (Exception, Error) as error:
                logger.warning(f'Update benchmark result failed, error: {error}')
                raise process_error(error)
            return
        else:
            raise process_error(error)

    try:
        diff_query = DIFF_QUERY_TEMPLATE.format(baseline_query, query, query, baseline_query)
        conn = get_db_connection(host=app.config.get('BENCHMARK_DB_HOST'), database=app.config.get('BENCHMARK_DB_NAME'),
                                 user=app.config.get('BENCHMARK_DB_USER'),
                                 password=app.config.get('BENCHMARK_DB_PASSWORD'),
                                 port=app.config.get('BENCHMARK_DB_PORT'),
                                 timeout=app.config.get('BENCHMARK_TIMEOUT') * 2, readonly=True)
        cur = execute_query(db_conn=conn, query=diff_query)
        result = cur.fetchall()[0][0]
        cur.close()
        conn.close()
        correctness = 'Correct' if result == 'Same' else 'Incorrect'
        logger.info(f'Benchmark query correctness: {correctness}')
    except (Exception, Error) as error:
        logger.warning(f'Benchmark diff query failed, error: {error}')
        raise process_error(error)

    is_correct = result == 'Same'
    dt = datetime.now(timezone.utc)
    planning_time = float(explain_result[-2][0].replace('Planning Time: ', '').replace(' ms', ''))
    execution_time = float(explain_result[-1][0].replace('Execution Time: ', '').replace(' ms', ''))
    total_time = planning_time + execution_time
    try:
        conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                 port=app.config.get('APP_DB_PORT'),
                                 user=app.config.get('APP_DB_USER'), password=app.config.get('APP_DB_PASSWORD'))
        cur = execute_query(db_conn=conn,
                            query='UPDATE submission SET is_correct = %s, updated_at = %s, planning_time = %s, execution_time = %s, total_time = %s WHERE submission_id = %s',
                            values=(is_correct, dt, planning_time, execution_time, total_time, submission_id))
        count = cur.rowcount
        cur.close()
        conn.close()
        logger.info(f"{count} records successfully updated for submission table")
    except (Exception, Error) as error:
        logger.warning(f'Update benchmark result failed, error: {error}')
        raise process_error(error)


class SubmissionList(Resource):
    @token_required
    def get(self):
        args = submission_list_parser.parse_args()
        user_name = args['user_name']
        challenge_id = args['challenge_id']
        try:
            query = 'SELECT s.user_name AS user_name, s.sql_query AS sql_query, s.submission_id AS submission_id, ' \
                    'c.challenge_name AS challenge_name, c.challenge_type AS challenge_type, ' \
                    'c.description AS description, s.created_at AS created_at, s.challenge_id AS challenge_id, ' \
                    's.planning_time AS planning_time, s.execution_time AS execution_time, ' \
                    's.total_time AS total_time, s.is_correct AS is_correct, s.error_message AS error_message, ' \
                    's.retry_times AS retry_times, c.is_deleted as is_deleted ' \
                    'FROM submission s join challenge c on s.challenge_id = c.challenge_id'
            values = ()
            if user_name and challenge_id:
                query = 'SELECT s.user_name AS user_name, s.sql_query AS sql_query, s.submission_id AS submission_id, ' \
                        'c.challenge_name AS challenge_name, c.challenge_type AS challenge_type, ' \
                        'c.description AS description, s.created_at AS created_at, s.challenge_id AS challenge_id, ' \
                        's.planning_time AS planning_time, s.execution_time AS execution_time, ' \
                        's.total_time AS total_time, s.is_correct AS is_correct, s.error_message AS error_message, ' \
                        's.retry_times AS retry_times, c.is_deleted as is_deleted ' \
                        'FROM submission s join challenge c on s.challenge_id = c.challenge_id ' \
                        'WHERE s.user_name = %s and s.challenge_id = %s'
                values = (user_name, challenge_id)
            elif user_name:
                query = 'SELECT s.user_name AS user_name, s.sql_query AS sql_query, s.submission_id AS submission_id, ' \
                        'c.challenge_name AS challenge_name, c.challenge_type AS challenge_type, ' \
                        'c.description AS description, s.created_at AS created_at, s.challenge_id AS challenge_id, ' \
                        's.planning_time AS planning_time, s.execution_time AS execution_time, ' \
                        's.total_time AS total_time, s.is_correct AS is_correct, s.error_message AS error_message, ' \
                        's.retry_times AS retry_times, c.is_deleted as is_deleted ' \
                        'FROM submission s join challenge c on s.challenge_id = c.challenge_id ' \
                        'WHERE s.user_name = %s'
                values = (user_name,)
            elif challenge_id:
                query = 'SELECT s.user_name AS user_name, s.sql_query AS sql_query, s.submission_id AS submission_id, ' \
                        'c.challenge_name AS challenge_name, c.challenge_type AS challenge_type, ' \
                        'c.description AS description, s.created_at AS created_at, s.challenge_id AS challenge_id, ' \
                        's.planning_time AS planning_time, s.execution_time AS execution_time, ' \
                        's.total_time AS total_time, s.is_correct AS is_correct, s.error_message AS error_message, ' \
                        's.retry_times AS retry_times, c.is_deleted as is_deleted ' \
                        'FROM submission s join challenge c on s.challenge_id = c.challenge_id ' \
                        'WHERE s.challenge_id = %s'
                values = (challenge_id,)
            conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                     user=app.config.get('APP_DB_USER'), port=app.config.get('APP_DB_PORT'),
                                     password=app.config.get('APP_DB_PASSWORD'), readonly=True)
            cur = execute_query(db_conn=conn, query=query, values=values)
            submission_list = cur.fetchall()
            cur.close()
            conn.close()
            submissions = []
            challenge_type = ''
            for submission in submission_list:
                submissions.append({'user_name': submission['user_name'], 'query': submission['sql_query'],
                                    'submission_id': submission['submission_id'],
                                    'challenge_name': submission['challenge_name'],
                                    'challenge_type': submission['challenge_type'],
                                    'challenge_description': submission['description'],
                                    'timestamp': submission['created_at'].strftime("%m/%d/%Y, %H:%M:%S"),
                                    'challenge_id': submission['challenge_id'],
                                    'planning_time': float(submission['planning_time']),
                                    'execution_time': float(submission['execution_time']),
                                    'total_time': float(submission['total_time']),
                                    'is_correct': submission['is_correct'],
                                    'error_message': submission['error_message'],
                                    'retry_times': submission['retry_times'],
                                    'is_deleted': submission['is_deleted']})
                challenge_type = submission['challenge_type']
            submissions = sorted(submissions, key=lambda k: k['is_correct'], reverse=True)
            submissions = sorted(submissions, key=lambda k: k['total_time'],
                                 reverse=(challenge_type == CHALLENGE_TYPE_SLOWEST_QUERY))
            submissions = sorted(submissions, key=lambda k: k['timestamp'], reverse=False)
            submissions = [dict(s, **{'rank': i}) for i, s in enumerate(submissions)]
            return make_response(jsonify(submissions), 200)
        except (Exception, Error) as error:
            print(f'Submission list query failed, error: {error}')
            return abort(400, message="Invalid Server Error")

    @token_required
    def post(self):
        args = submission_parser.parse_args()
        query = args['query'].replace(';', '').lower().strip()
        if not query.startswith('select'):
            return abort(400, message="Only Select Query Allowed")
        if not validate_sql_syntax(query):
            return abort(400, message="Invalid Query Syntax")
        name = args['user_name']
        challenge_id = args['challenge_id']
        # challenge id must be valid, i.e. a challenge with this id must exist
        try:
            # challenge id must be valid, i.e. a challenge with this id must exist
            conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                     user=app.config.get('APP_DB_USER'), port=app.config.get('APP_DB_PORT'),
                                     password=app.config.get('APP_DB_PASSWORD'))
            cur = execute_query(db_conn=conn, query='SELECT * FROM challenge WHERE challenge_id = %s',
                                values=(challenge_id,))
            challenge = cur.fetchone()
            cur.close()
            conn.close()
        except (Exception, Error) as error:
            print(f'Submission query challenge failed, error: {error}')
            return abort(500, message="Internal Server Error")
        if not challenge:
            return abort(404, message=f"Challenge {challenge_id} doesn't exist")
        elif challenge['is_deleted']:
            return abort(400, message=f"Challenge {challenge_id} already deleted")
        try:
            dt = datetime.now(timezone.utc)
            submission_id = 'sub_' + str(uuid.uuid4())
            prepared_query = """ INSERT INTO submission (submission_id, user_name, created_at, updated_at, challenge_id, sql_query) VALUES (%s, %s, %s, %s, %s, %s)"""
            record = (submission_id, name, dt, dt, challenge_id, query)
            conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                     user=app.config.get('APP_DB_USER'), port=app.config.get('APP_DB_PORT'),
                                     password=app.config.get('APP_DB_PASSWORD'))
            cur = execute_query(db_conn=conn, query=prepared_query, values=record)
            count = cur.rowcount
            print(f"{count} records inserted successfully into submission table")
            cur.close()
            conn.close()
        except (Exception, Error) as error:
            print(f'Submission insertion failed, error: {error}')
            return abort(500, message="Internal Server Error")

        benchmark_query.delay(baseline_query=challenge['sql_query'], query=query, submission_id=submission_id)
        return make_response(jsonify({'user_name': name, 'query': query, 'submission_id': submission_id,
                                      'time_stamp': dt.strftime("%m/%d/%Y, %H:%M:%S")}), 201)


class Submission(Resource):
    @token_required
    def get(self, submission_id):
        try:
            conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                     user=app.config.get('APP_DB_USER'), port=app.config.get('APP_DB_PORT'),
                                     password=app.config.get('APP_DB_PASSWORD'), readonly=True)
            query = 'SELECT s.user_name AS user_name, s.sql_query AS sql_query, s.submission_id AS submission_id, ' \
                    'c.challenge_name AS challenge_name, c.challenge_type AS challenge_type, ' \
                    'c.description AS description, s.created_at AS created_at, s.challenge_id AS challenge_id, ' \
                    's.planning_time AS planning_time, s.execution_time AS execution_time, ' \
                    's.total_time AS total_time, s.is_correct AS is_correct, s.error_message AS error_message, ' \
                    's.retry_times AS retry_times, c.is_deleted as is_deleted ' \
                    'FROM submission s join challenge c on s.challenge_id = c.challenge_id ' \
                    'WHERE s.submission_id = %s'
            cur = execute_query(db_conn=conn,
                                query=query,
                                values=(submission_id,))
            submission = cur.fetchone()
            cur.close()
            conn.close()
        except (Exception, Error) as error:
            print(f'Submission query submission failed, error: {error}')
            return abort(400, message="Invalid Server Error")
        if submission is None:
            return abort(404, message=f"Submission {submission_id} doesn't exist")
        return make_response(jsonify({'user_name': submission['user_name'], 'query': submission['sql_query'],
                                      'submission_id': submission_id,
                                      'challenge_name': submission["challenge_name"],
                                      'challenge_type': submission['challenge_type'],
                                      'challenge_description': submission['description'],
                                      'timestamp': submission['created_at'].strftime("%m/%d/%Y, %H:%M:%S"),
                                      'challenge_id': submission['challenge_id'],
                                      'planning_time': float(submission['planning_time']),
                                      'total_time': float(submission['total_time']),
                                      'execution_time': float(submission['execution_time']),
                                      'is_correct': submission['is_correct'],
                                      'error_message': submission['error_message'],
                                      'retry_times': submission['retry_times'],
                                      'is_deleted': submission['is_deleted']}), 200)


class ChallengeList(Resource):
    @token_required
    def get(self):
        args = challenge_list_parser.parse_args()
        user_name = args['user_name']
        try:
            conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                     user=app.config.get('APP_DB_USER'), port=app.config.get('APP_DB_PORT'),
                                     password=app.config.get('APP_DB_PASSWORD'), readonly=True)
            base_query = 'SELECT c1.user_name as user_name, c1.sql_query as sql_query, ' \
                         'c1.challenge_name as challenge_name, c1.description as challenge_description, ' \
                         'c2.description as challenge_type_description, c1.challenge_type as challenge_type, ' \
                         'c1.challenge_id as challenge_id, c1.created_at as created_at, c1.is_deleted as is_deleted' \
                         ' FROM challenge c1 JOIN challenge_type c2 ON c1.challenge_type = c2.challenge_type'
            filtered_query = base_query + ' WHERE c1.user_name = %s'
            cur = execute_query(db_conn=conn, query=filtered_query,
                                values=(user_name,)) if user_name else execute_query(db_conn=conn,
                                                                                     query=base_query)
            challenge_list = cur.fetchall()
            cur.close()
            conn.close()
            challenges = []
            for challenge in challenge_list:
                challenges.append({'user_name': challenge['user_name'], 'query': challenge['sql_query'],
                                   'challenge_id': challenge["challenge_id"],
                                   'challenge_name': challenge["challenge_name"],
                                   'challenge_type': challenge["challenge_type"],
                                   'challenge_description': challenge["challenge_description"],
                                   'challenge_type_description': challenge["challenge_type_description"],
                                   'timestamp': challenge['created_at'].strftime("%m/%d/%Y, %H:%M:%S"),
                                   'is_deleted': challenge['is_deleted']})
            return make_response(jsonify(challenges), 200)
        except (Exception, Error) as error:
            print(f'Challenge list query failed, error: {error}')
            return abort(500, message="Internal Server Error")

    @token_required
    def post(self):
        args = challenge_parser.parse_args()
        query = args['query'].replace(';', '').lower().strip()
        challenge_name = args['challenge_name'].strip()
        challenge_type = args['challenge_type']
        challenge_description = args['challenge_description']
        if not query.startswith('select'):
            return abort(400, message="Only Select Query Allowed")
        if not validate_sql_syntax(query):
            return abort(400, message="Invalid Query Syntax")
        name = args['user_name']

        try:
            can_access = check_admin(name)
        except (Exception, Error) as error:
            print('Challenge check privilege failed, error:', error)
            return abort(500, message="Internal Server Error")
        if not can_access:
            return abort(403, message=f"User {name} is forbidden to access this API")
        try:
            dt = datetime.now(timezone.utc)
            challenge_id = 'ch_' + str(uuid.uuid4())
            prepared_query = """ INSERT INTO challenge (user_name, created_at, updated_at, challenge_id, challenge_name, challenge_type, description, sql_query) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            record = (name, dt, dt, challenge_id, challenge_name, challenge_type, challenge_description, query)
            conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                     user=app.config.get('APP_DB_USER'), port=app.config.get('APP_DB_PORT'),
                                     password=app.config.get('APP_DB_PASSWORD'))
            cur = execute_query(db_conn=conn, query=prepared_query, values=record)
            count = cur.rowcount
            print(f"{count} records inserted successfully into challenge table")
            cur.close()
            conn.close()
        except (Exception, Error) as error:
            print('Challenge insertion failed, error:', error)
            return abort(500, message="Internal Server Error")
        return make_response(jsonify({'user_name': name, 'query': query, 'challenge_id': challenge_id,
                                      'challenge_name': challenge_name, 'challenge_type': challenge_type,
                                      'challenge_description': challenge_description,
                                      'time_stamp': dt.strftime("%m/%d/%Y, %H:%M:%S")}), 201)


class Challenge(Resource):
    @token_required
    def get(self, challenge_id):
        try:
            conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                     user=app.config.get('APP_DB_USER'), port=app.config.get('APP_DB_PORT'),
                                     password=app.config.get('APP_DB_PASSWORD'), readonly=True)
            query = 'SELECT c1.user_name as user_name, c1.sql_query as sql_query, ' \
                    'c1.challenge_name as challenge_name, c1.description as challenge_description, ' \
                    'c2.description as challenge_type_description, c1.challenge_type as challenge_type, ' \
                    'c1.created_at as created_at, c1.is_deleted as is_deleted' \
                    ' FROM challenge c1 JOIN challenge_type c2 ON c1.challenge_type = c2.challenge_type ' \
                    'WHERE challenge_id = %s'
            cur = execute_query(db_conn=conn, query=query,
                                values=(challenge_id,))
            challenge = cur.fetchone()
            cur.close()
            conn.close()
        except (Exception, Error) as error:
            print(f'Challenge query failed, error: {error}')
            return abort(500, message="Internal Server Error")
        if not challenge:
            return abort(404, message=f"Challenge {challenge_id} doesn't exist")
        return make_response(jsonify({'user_name': challenge['user_name'], 'query': challenge['sql_query'],
                                      'challenge_id': challenge_id,
                                      'challenge_name': challenge["challenge_name"],
                                      'challenge_type': challenge["challenge_type"],
                                      'challenge_description': challenge["challenge_description"],
                                      'challenge_type_description': challenge["challenge_type_description"],
                                      'timestamp': challenge['created_at'].strftime("%m/%d/%Y, %H:%M:%S"),
                                      'is_deleted': challenge['is_deleted']}), 200)

    @token_required
    def delete(self, challenge_id):
        try:
            dt = datetime.now(timezone.utc)
            conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                     user=app.config.get('APP_DB_USER'),
                                     port=app.config.get('APP_DB_PORT'),
                                     password=app.config.get('APP_DB_PASSWORD'))
            cur = execute_query(db_conn=conn,
                                query="UPDATE challenge SET updated_at = %s, is_deleted = %s WHERE challenge_id = %s",
                                values=(dt, True, challenge_id))
            count = cur.rowcount
            cur.close()
            conn.close()
            logger.info(f"{count} records successfully updated for challenge table")
        except (Exception, Error) as error:
            logger.warning(f'Update challenge failed, error: {error}')
            raise process_error(error)
        return make_response(jsonify({}), 204)


class ChallengeTypeList(Resource):
    @token_required
    def get(self):
        try:
            conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                     user=app.config.get('APP_DB_USER'), port=app.config.get('APP_DB_PORT'),
                                     password=app.config.get('APP_DB_PASSWORD'), readonly=True)
            cur = execute_query(db_conn=conn, query='SELECT * FROM challenge_type')
            challenge_type_list = cur.fetchall()
            cur.close()
            conn.close()
            challenge_types = []
            for challenge_type in challenge_type_list:
                challenge_types.append(
                    {'user_name': challenge_type['user_name'], 'challenge_type': challenge_type['challenge_type'],
                     'description': challenge_type["description"],
                     'timestamp': challenge_type['created_at'].strftime("%m/%d/%Y, %H:%M:%S")})
            return make_response(jsonify(challenge_types), 200)
        except (Exception, Error) as error:
            print(f'Challenge type list query failed, error: {error}')
            return abort(500, message="Internal Server Error")

    @token_required
    def post(self):
        args = challenge_type_parser.parse_args()
        challenge_type = args['challenge_type']
        description = args['description'].strip()
        name = args['user_name']
        try:
            can_access = check_admin(name)
        except (Exception, Error) as error:
            print('Challenge type check privilege failed, error:', error)
            return abort(500, message="Internal Server Error")

        if not can_access:
            abort(403, message=f"User {name} is forbidden to access this API")

        try:
            dt = datetime.now(timezone.utc)
            prepared_query = """ INSERT INTO challenge_type (user_name, created_at, updated_at, challenge_type, description) VALUES (%s, %s, %s, %s, %s)"""
            record = (name, dt, dt, challenge_type, description)
            conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                     user=app.config.get('APP_DB_USER'), port=app.config.get('APP_DB_PORT'),
                                     password=app.config.get('APP_DB_PASSWORD'))
            cur = execute_query(db_conn=conn, query=prepared_query, values=record)
            count = cur.rowcount
            print(f"{count} records inserted successfully into challenge type table")
            cur.close()
            conn.close()
        except (Exception, Error) as error:
            print('Challenge type insertion failed, error:', error)
            return abort(500, message="Internal Server Error")
        return make_response(jsonify({'user_name': name, 'challenge_type': challenge_type,
                                      'description': description,
                                      'time_stamp': dt.strftime("%m/%d/%Y, %H:%M:%S")}), 201)


class ChallengeType(Resource):
    @token_required
    def get(self, challenge_type):
        try:
            conn = get_db_connection(host=app.config.get('APP_DB_HOST'), database=app.config.get('APP_DB_NAME'),
                                     user=app.config.get('APP_DB_USER'), port=app.config.get('APP_DB_PORT'),
                                     password=app.config.get('APP_DB_PASSWORD'), readonly=True)
            cur = execute_query(db_conn=conn, query='SELECT * FROM challenge_type WHERE challenge_type = %s',
                                values=(challenge_type,))
            record = cur.fetchone()
            cur.close()
            conn.close()
        except (Exception, Error) as error:
            print(f'Challenge type query failed, error: {error}')
            return abort(500, message="Internal Server Error")
        if not record:
            return abort(404, message=f"Challenge type {challenge_type} doesn't exist")
        return make_response(jsonify({'user_name': record['user_name'], 'challenge_type': record['challenge_type'],
                                      'description': record["description"],
                                      'timestamp': record['created_at'].strftime("%m/%d/%Y, %H:%M:%S")}), 200)


api.add_resource(Submission, '/submission/<submission_id>')
api.add_resource(SubmissionList, '/submissions')
api.add_resource(Challenge, '/challenge/<challenge_id>')
api.add_resource(ChallengeList, '/challenges')
api.add_resource(ChallengeType, '/challenge_type/<challenge_type>')
api.add_resource(ChallengeTypeList, '/challenge_types')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(debug=True)
