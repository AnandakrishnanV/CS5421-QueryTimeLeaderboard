import uuid
from datetime import datetime, timezone
import sqlvalidator
from celery.utils.log import get_task_logger

from flask import Flask
from flask_restful import reqparse, Resource, Api, abort
from psycopg2 import Error
from celery import Celery
from db_client import get_db_connection, execute_query
from util import RetryableError, BenchMarkTask, process_error, NonRetryableError

# TODO: receive configs and credentials via command line arguments or environment variables


# create readonly user or grant only select permission for executing benchmarking queries to avoid injection
# write permission is given to admin users like the professor or TAs

app = Flask(__name__)
api = Api(app)
logger = get_task_logger(__name__)

app.config['celery_broker_url'] = 'redis://localhost:6379'
app.config['celery_result_backend'] = 'redis://localhost:6379'

celery = Celery(app.name, broker=app.config['celery_broker_url'], backend=app.config['celery_result_backend'])
celery.conf.update(app.config)

# should use a different database server
BENCHMARK_TIMEOUT = 1

challenge_parser = reqparse.RequestParser()
challenge_parser.add_argument('user_name', type=str, required=True, help="User name cannot be blank!")
challenge_parser.add_argument('query', type=str, required=True, help="Query cannot be blank!")

submission_parser = reqparse.RequestParser()
submission_parser.add_argument('query', type=str, required=True, help="Query cannot be blank!")
submission_parser.add_argument('user_name', type=str, required=True, help="User name cannot be blank!")
submission_parser.add_argument('challenge_id', type=str, required=True, help="Challenge ID cannot be blank!")

DIFF_QUERY_TEMPLATE = '''SELECT CASE WHEN COUNT(*) = 0 THEN 'Same' ELSE 'Different' END FROM (({} EXCEPT {}) UNION ({} EXCEPT {})) AS RESULT'''


def validate_sql_syntax(query: str):
    sql_query = sqlvalidator.parse(query)
    if not sql_query.is_valid():
        print(f'invalid query: {query}, errors: {sql_query.errors}')
        return False
    return True


@celery.task(throws=(RetryableError,NonRetryableError), autoretry_for=(RetryableError,), retry_backoff=True, max_retries=10, base=BenchMarkTask)
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
                                    query=f"UPDATE submission SET updated_at = '{dt}', error_message = 'query timeout' WHERE submission_id = '{submission_id}'")
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
        conn = get_db_connection(host='localhost', database='tuning', user='test', password='test',
                                 timeout=BENCHMARK_TIMEOUT*2, readonly=True)
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
    planning_time = int(float(explain_result[-2][0].replace('Planning Time: ', '').replace(' ms', '')) * 1000)
    execution_time = int(float(explain_result[-1][0].replace('Execution Time: ', '').replace(' ms', '')) * 1000)
    try:
        conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
        cur = execute_query(db_conn=conn,
                            query=f"UPDATE submission SET is_correct = {is_correct}, updated_at = '{dt}', planning_time = {planning_time}, execution_time = {execution_time} WHERE submission_id = '{submission_id}'")
        count = cur.rowcount
        cur.close()
        conn.close()
        logger.info(f"{count} records successfully updated for submission table")
    except (Exception, Error) as error:
        logger.warning(f'Update benchmark result failed, error: {error}')
        raise process_error(error)


class Submission(Resource):
    def get(self, submission_id):
        submission_id = f"'{submission_id}'"
        try:
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
            cur = execute_query(db_conn=conn, query=f'SELECT * FROM submission WHERE submission_id = {submission_id}')
            submission = cur.fetchone()
            cur.close()
            conn.close()
            if submission is None:
                abort(404, message="Submission {} doesn't exist".format(submission_id))
            return {'user_name': submission['user_name'], 'query': submission['sql_query'],
                    'submission_id': submission_id,
                    'timestamp': submission['created_at'].strftime("%m/%d/%Y, %H:%M:%S"),
                    'challenge_id': submission['challenge_id'], 'planning_time': submission['planning_time'],
                    'execution_time': submission['execution_time'], 'is_correct': submission['is_correct']}, 200
        except (Exception, Error) as error:
            print(f'Submission query submission failed, error: {error}')
            return abort(400, message="Invalid Server Error")

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
        quoted_challenge_id = f"'{challenge_id}'"
        try:
            # challenge id must be valid, i.e. a challenge with this id must exist
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
            cur = execute_query(db_conn=conn, query=f'SELECT * FROM challenge WHERE challenge_id = {quoted_challenge_id}')
            challenge = cur.fetchone()
            cur.close()
            conn.close()
            if not challenge:
                abort(404, message="Challenge {} doesn't exist".format(challenge_id))
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


class Challenge(Resource):
    def get(self, challenge_id):
        challenge_id = f"'{challenge_id}'"
        challenge = None
        try:
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
            cur = execute_query(db_conn=conn, query=f'SELECT * FROM challenge WHERE challenge_id = {challenge_id}')
            challenge = cur.fetchone()
            cur.close()
            conn.close()
        except (Exception, Error):
            return abort(500, message="Internal Server Error")

        if not challenge:
            abort(404, message="Challenge {} doesn't exist".format(challenge_id))
        return {'user_name': challenge['user_name'], 'query': challenge['sql_query'], 'challenge_id': challenge_id,
                'timestamp': challenge['created_at'].strftime("%m/%d/%Y, %H:%M:%S")}, 200

    def post(self):
        args = challenge_parser.parse_args()
        query = args['query'].replace(';', '').lower().strip()
        if not query.startswith('select'):
            return abort(400, message="Only Select Query Allowed")
        if not validate_sql_syntax(query):
            return abort(400, message="Invalid Query Syntax")
        name = args['user_name']
        try:
            dt = datetime.now(timezone.utc)
            challenge_id = 'ch_' + str(uuid.uuid4())
            prepared_query = """ INSERT INTO challenge (user_name, created_at, updated_at, challenge_id, sql_query) VALUES (%s, %s, %s, %s, %s)"""
            record = (name, dt, dt, challenge_id, query)
            conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
            cur = execute_query(db_conn=conn, query=prepared_query, values=record)
            count = cur.rowcount
            print(f"{count} records inserted successfully into challenge table")
            cur.close()
            conn.close()
        except (Exception, Error) as error:
            print('Challenge insertion failed, error:', error)
            return abort(500, message="Internal Server Error")
        return {'user_name': name, 'query': query, 'challenge_id': challenge_id,
                'time_stamp': dt.strftime("%m/%d/%Y, %H:%M:%S")}, 201


api.add_resource(Submission, '/submissions', '/submissions/<submission_id>')
api.add_resource(Challenge, '/challenges', '/challenges/<challenge_id>')

if __name__ == '__main__':
    app.run(debug=True)
