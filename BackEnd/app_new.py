import uuid
import jwt
from datetime import datetime, timezone, timedelta
from celery.utils.log import get_task_logger

from flask import Flask, request,  jsonify, flash, session ,make_response
from flask_restful import reqparse, Resource, Api, abort
from psycopg2 import Error
from celery import Celery
from db_client import get_db_connection, execute_query, validate_sql_syntax
from util import RetryableError, BenchMarkTask, process_error, NonRetryableError
from functools import wraps
from werkzeug.security import generate_password_hash,check_password_hash

# TODO: receive configs and credentials via command line arguments or environment variables


# create readonly user or grant only select permission for executing benchmarking queries to avoid injection
# write permission is given to admin users like the professor or TAs

app = Flask(__name__)
api = Api(app)
logger = get_task_logger(__name__)

app.config['celery_broker_url'] = 'redis://localhost:6379'
app.config['celery_result_backend'] = 'redis://localhost:6379'

app.config['SECRET_KEY'] = '8454e5a14e6c4a3490e85f8cd0737fa0'

celery = Celery(app.name, broker=app.config['celery_broker_url'], backend=app.config['celery_result_backend'])
celery.conf.update(app.config)

# should use a different database server
BENCHMARK_TIMEOUT = 5000

challenge_parser = reqparse.RequestParser()
challenge_parser.add_argument('user_name', type=str, required=True, help="User name cannot be blank!")
challenge_parser.add_argument('query', type=str, required=True, help="Query cannot be blank!")
challenge_parser.add_argument('challenge_name', type=str, required=True, help="Challenge name cannot be blank!")
challenge_parser.add_argument('challenge_type', type=int, required=True, help="Challenge type cannot be blank!")
challenge_parser.add_argument('challenge_description', type=str, required=True, help="Challenge description cannot be blank!")

submission_parser = reqparse.RequestParser()
submission_parser.add_argument('query', type=str, required=True, help="Query cannot be blank!")
submission_parser.add_argument('user_name', type=str, required=True, help="User name cannot be blank!")
submission_parser.add_argument('challenge_id', type=str, required=True, help="Challenge ID cannot be blank!")

submission_list_parser = reqparse.RequestParser()
submission_list_parser.add_argument('user_name', type=str)
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
    # decorator factory which invoks update_wrapper() method and passes decorated function as an argument
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])

        except:
            return jsonify({'Message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return decorated


class Login(Resource):
    def post(self):

        args = login_parser.parse_args()
        user_name = args['user_name']
        password=args['password']
        # to generate the hashed password, use generate_password_hash(<password str>, method='sha256')

        try:
            conn = get_db_connection(host='localhost', database='tuning', user='davide', password='jw8s0F4',
                                     readonly=True)
            cur = execute_query(db_conn=conn, query='SELECT * FROM users WHERE user_name = %s ',
                                values=(user_name,))

            current_user= cur.fetchall()
            hashed_password=current_user[0][-2]
            cur.close()
            conn.close()

            if current_user and check_password_hash(hashed_password,password):
                session['logged_in'] = True

                token = jwt.encode({
                    'user': user_name,
                    'exp': datetime.utcnow() + timedelta(minutes=30)
                },
                    app.config['SECRET_KEY'])
                return jsonify({'token': token})
            else:
                return make_response('Unable to verify', 403,
                                     {'WWW-Authenticate': 'Basic realm: "Authentication Failed "'})
        except (Exception, Error) as error:
            print(f'Login check failed, error: {error}')
            return abort(500, message="Internal Server Error")

@celery.task(throws=(RetryableError, NonRetryableError), autoretry_for=(RetryableError,), retry_backoff=True,
             max_retries=10, base=BenchMarkTask)
def benchmark_query(baseline_query: str, query: str, submission_id):
    explain_result = None
    try:
        conn = get_db_connection(host='localhost', database='tuning', user='read_user', password='read_user',
                                 timeout=BENCHMARK_TIMEOUT, readonly=True)
        cur = execute_query(db_conn=conn, query=f"EXPLAIN ANALYZE {query}")
        explain_result = cur.fetchall()
        logger.info(f'Benchmark result, {explain_result[-2][0]}, {explain_result[-1][0]}')
        cur.close()
        conn.close()
    except (Exception, Error) as error:
        logger.warning(f'Benchmark query failed, error: {error}')
        if 'canceling statement due to statement timeout' in str(error):
            logger.warning(
                f'Benchmark result maximum total time {BENCHMARK_TIMEOUT}ms for planning and execution reached')
            # still update on timeout
            try:
                dt = datetime.now(timezone.utc)
                conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
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

    result = None
    try:
        diff_query = DIFF_QUERY_TEMPLATE.format(baseline_query, query, query, baseline_query)
        conn = get_db_connection(host='localhost', database='tuning', user='read_user', password='read_user',
                                 timeout=BENCHMARK_TIMEOUT * 2, readonly=True)
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
    planning_time = explain_result[-2][0].replace('Planning Time: ', '').replace(' ms', '')
    execution_time = explain_result[-1][0].replace('Execution Time: ', '').replace(' ms', '')
    try:
        conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
        cur = execute_query(db_conn=conn,
                            query='UPDATE submission SET is_correct = %s, updated_at = %s, planning_time = %s, execution_time = %s WHERE submission_id = %s',
                            values=(is_correct, dt, planning_time, execution_time, submission_id))
        count = cur.rowcount
        cur.close()
        conn.close()
        logger.info(f"{count} records successfully updated for submission table")
    except (Exception, Error) as error:
        logger.warning(f'Update benchmark result failed, error: {error}')
        raise process_error(error)


class SubmissionList(Resource):
    def get(self):
        args = submission_list_parser.parse_args()
        user_name = args['user_name']
        try:
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test', readonly=True)
            cur = execute_query(db_conn=conn, query='SELECT * FROM submission WHERE user_name = %s',
                                values=(user_name,)) if user_name else execute_query(db_conn=conn,
                                                                                     query='SELECT * FROM submission')
            submission_list = cur.fetchall()
            cur.close()
            conn.close()
            submissions = []
            for submission in submission_list:
                submissions.append({'user_name': submission['user_name'], 'query': submission['sql_query'],
                                    'submission_id': submission['submission_id'],
                                    'timestamp': submission['updated_at'].strftime("%m/%d/%Y, %H:%M:%S"),
                                    'challenge_id': submission['challenge_id'],
                                    'planning_time': float(submission['planning_time']),
                                    'execution_time': float(submission['execution_time']),
                                    'is_correct': submission['is_correct'],
                                    'error_message': submission['error_message'],
                                    'retry_times': submission['retry_times']})
            return submissions, 200
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
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
            cur = execute_query(db_conn=conn, query='SELECT * FROM challenge WHERE challenge_id = %s',
                                values=(challenge_id,))
            challenge = cur.fetchone()
            cur.close()
            conn.close()
            if not challenge:
                return abort(404, message=f"Challenge {challenge_id} doesn't exist")
        except (Exception, Error) as error:
            print(f'Submission query challenge failed, error: {error}')
            return abort(500, message="Internal Server Error")
        try:
            dt = datetime.now(timezone.utc)
            submission_id = 'sub_' + str(uuid.uuid4())
            prepared_query = """ INSERT INTO submission (submission_id, user_name, created_at, updated_at, challenge_id, sql_query) VALUES (%s, %s, %s, %s, %s, %s)"""
            record = (submission_id, name, dt, dt, challenge_id, query)
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
            cur = execute_query(db_conn=conn, query=prepared_query, values=record)
            count = cur.rowcount
            print(f"{count} records inserted successfully into submission table")
            cur.close()
            conn.close()
        except (Exception, Error) as error:
            print(f'Submission insertion failed, error: {error}')
            return abort(500, message="Internal Server Error")

        benchmark_query.delay(baseline_query=challenge['sql_query'], query=query, submission_id=submission_id)
        return {'user_name': name, 'query': query, 'submission_id': submission_id,
                'time_stamp': dt.strftime("%m/%d/%Y, %H:%M:%S")}, 201


class Submission(Resource):
    def get(self, submission_id):
        try:
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test', readonly=True)
            cur = execute_query(db_conn=conn, query='SELECT * FROM submission WHERE submission_id = %s',
                                values=(submission_id,))
            submission = cur.fetchone()
            cur.close()
            conn.close()
            if submission is None:
                return abort(404, message=f"Submission {submission_id} doesn't exist")
            return {'user_name': submission['user_name'], 'query': submission['sql_query'],
                    'submission_id': submission_id,
                    'timestamp': submission['updated_at'].strftime("%m/%d/%Y, %H:%M:%S"),
                    'challenge_id': submission['challenge_id'], 'planning_time': float(submission['planning_time']),
                    'execution_time': float(submission['execution_time']), 'is_correct': submission['is_correct'],
                    'error_message': submission['error_message'], 'retry_times': submission['retry_times']}, 200
        except (Exception, Error) as error:
            print(f'Submission query submission failed, error: {error}')
            return abort(400, message="Invalid Server Error")


class ChallengeList(Resource):
    def get(self):
        args = challenge_list_parser.parse_args()
        user_name = args['user_name']
        try:
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test', readonly=True)
            cur = execute_query(db_conn=conn, query='SELECT * FROM challenge WHERE user_name = %s',
                                values=(user_name,)) if user_name else execute_query(db_conn=conn,
                                                                                     query='SELECT * FROM challenge')
            challenge_list = cur.fetchall()
            cur.close()
            conn.close()
            challenges = []
            for challenge in challenge_list:
                try:
                    type_conn = get_db_connection(host='localhost', database='tuning', user='test', password='test',
                                                  readonly=True)
                    type_cur = execute_query(db_conn=type_conn,
                                             query='SELECT * FROM challenge_type WHERE challenge_type = %s',
                                             values=(challenge["challenge_type"],))
                    challenge_type = type_cur.fetchone()
                    type_cur.close()
                    type_conn.close()
                    challenges.append({'user_name': challenge['user_name'], 'query': challenge['sql_query'],
                                       'challenge_id': challenge["challenge_id"],
                                       'challenge_name': challenge["challenge_name"],
                                       'challenge_type': challenge["challenge_type"],
                                       'challenge_description': challenge["description"],
                                       'challenge_type_description': challenge_type["description"],
                                       'timestamp': challenge['updated_at'].strftime("%m/%d/%Y, %H:%M:%S")})

                except (Exception, Error) as error:
                    print(f'Challenge list query challenge type failed, error: {error}')
                    return abort(500, message="Internal Server Error")
            return challenges, 200
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
            dt = datetime.now(timezone.utc)
            challenge_id = 'ch_' + str(uuid.uuid4())
            admin_query = 'SELECT is_admin FROM users WHERE user_name = %s'
            prepared_query = """ INSERT INTO challenge (user_name, created_at, updated_at, challenge_id, challenge_name, challenge_type, description, sql_query) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            record = (name, dt, dt, challenge_id, challenge_name, challenge_type, challenge_description, query)
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
            cur_is_admin = execute_query(db_conn=conn, query=admin_query, values=(name,))
            is_admin = cur_is_admin.fetchone()
            if is_admin[0]:
                cur = execute_query(db_conn=conn, query=prepared_query, values=record)
                count = cur.rowcount
                print(f"{count} records inserted successfully into challenge table")
            else:
                return abort(403, message=f"User {name} is not allowed to update here")
            cur_is_admin.close()
            cur.close()
            conn.close()
        except (Exception, Error) as error:
            print('Challenge insertion failed, error:', error)
            return abort(500, message="Internal Server Error")
        return {'user_name': name, 'query': query, 'challenge_id': challenge_id,
                'challenge_name': challenge_name, 'challenge_type': challenge_type,
                'challenge_description': challenge_description,
                'time_stamp': dt.strftime("%m/%d/%Y, %H:%M:%S")}, 201


class Challenge(Resource):
    def get(self, challenge_id):
        try:
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test', readonly=True)
            cur = execute_query(db_conn=conn, query='SELECT * FROM challenge WHERE challenge_id = %s',
                                values=(challenge_id,))
            challenge = cur.fetchone()
            cur.close()
            conn.close()
            if not challenge:
                return abort(404, message=f"Challenge {challenge_id} doesn't exist")
            try:
                type_conn = get_db_connection(host='localhost', database='tuning', user='test', password='test',
                                              readonly=True)
                type_cur = execute_query(db_conn=type_conn,
                                         query='SELECT * FROM challenge_type WHERE challenge_type = %s',
                                         values=(challenge["challenge_type"],))
                challenge_type = type_cur.fetchone()
                type_cur.close()
                type_conn.close()
                return {'user_name': challenge['user_name'], 'query': challenge['sql_query'],
                        'challenge_id': challenge_id,
                        'challenge_name': challenge["challenge_name"], 'challenge_type': challenge["challenge_type"],
                        'challenge_description': challenge["description"],
                        'challenge_type_description': challenge_type["description"],
                        'timestamp': challenge['updated_at'].strftime("%m/%d/%Y, %H:%M:%S")}, 200
            except (Exception, Error) as error:
                print(f'Challenge query challenge type failed, error: {error}')
                return abort(500, message="Internal Server Error")
        except (Exception, Error) as error:
            print(f'Challenge query failed, error: {error}')
            return abort(500, message="Internal Server Error")


class ChallengeTypeList(Resource):
    def get(self):
        try:
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test', readonly=True)
            cur = execute_query(db_conn=conn, query='SELECT * FROM challenge_type')
            challenge_type_list = cur.fetchall()
            cur.close()
            conn.close()
            challenge_types = []
            for challenge_type in challenge_type_list:
                challenge_types.append(
                    {'user_name': challenge_type['user_name'], 'challenge_type': challenge_type['challenge_type'],
                     'description': challenge_type["description"],
                     'timestamp': challenge_type['updated_at'].strftime("%m/%d/%Y, %H:%M:%S")})
            return challenge_types, 200
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
            dt = datetime.now(timezone.utc)
            admin_query = 'SELECT is_admin FROM users WHERE user_name = %s'
            prepared_query = """ INSERT INTO challenge_type (user_name, created_at, updated_at, challenge_type, description) VALUES (%s, %s, %s, %s, %s)"""
            record = (name, dt, dt, challenge_type, description)
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
            cur_is_admin = execute_query(db_conn=conn, query=admin_query, values=(name,))
            is_admin = cur_is_admin.fetchone()
            if is_admin[0]:
                cur = execute_query(db_conn=conn, query=prepared_query, values=record)
                count = cur.rowcount
                print(f"{count} records inserted successfully into challenge type table")
            else:
                return abort(403, message=f"User {name} is not allowed to update here")
            cur_is_admin.close()
            cur.close()
            conn.close()
        except (Exception, Error) as error:
            print('Challenge type insertion failed, error:', error)
            return abort(500, message="Internal Server Error")
        return {'user_name': name, 'challenge_type': challenge_type,
                'description': description,
                'time_stamp': dt.strftime("%m/%d/%Y, %H:%M:%S")}, 201


class ChallengeType(Resource):
    def get(self, challenge_type):
        try:
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test', readonly=True)
            cur = execute_query(db_conn=conn, query='SELECT * FROM challenge_type WHERE challenge_type = %s',
                                values=(challenge_type,))
            record = cur.fetchone()
            cur.close()
            conn.close()
            if not record:
                return abort(404, message=f"Challenge type {challenge_type} doesn't exist")
            return {'user_name': record['user_name'], 'challenge_type': record['challenge_type'],
                    'description': record["description"],
                    'timestamp': record['updated_at'].strftime("%m/%d/%Y, %H:%M:%S")}, 200
        except (Exception, Error) as error:
            print(f'Challenge type query failed, error: {error}')
            return abort(500, message="Internal Server Error")


api.add_resource(Submission, '/submission/<submission_id>')
api.add_resource(SubmissionList, '/submissions')
api.add_resource(Challenge, '/challenge/<challenge_id>')
api.add_resource(ChallengeList, '/challenges')
api.add_resource(ChallengeType, '/challenge_type/<challenge_type>')
api.add_resource(ChallengeTypeList, '/challenge_types')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(debug=True)
