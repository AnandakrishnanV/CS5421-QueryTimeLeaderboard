import uuid
from datetime import datetime, timezone, date
import sqlvalidator

import psycopg2
import psycopg2.extras
from flask import Flask
from flask_restful import reqparse, Resource, Api, abort
from psycopg2 import Error


def get_db_connection(host: str, database: str, user: str, password: str, timeout: int = 5000):
    options = f'-c statement_timeout={timeout}'
    conn = psycopg2.connect(host=host,
                            database=database,
                            user=user,
                            password=password, options=options)
    return conn


app = Flask(__name__)
api = Api(app)

submission_conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
challenge_conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')

# should use a different database server
BENCHMARK_TIMEOUT = 5000
benchmark_conn = get_db_connection(host='localhost', database='tuning', user='test', password='test',
                                   timeout=BENCHMARK_TIMEOUT)

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


# TODO: make this async using task queue or crontab
def benchmark_query(baseline_query: str, query: str):
    cur = benchmark_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    explain_query = f"EXPLAIN ANALYZE {query}"
    try:
        cur.execute(explain_query)
    except (Exception, Error) as error:
        print(f'Benchmark query failed, error: {error}')
        if 'canceling statement due to statement timeout' in str(error):
            print(f'Benchmark result maximum total time {BENCHMARK_TIMEOUT}ms for planning and execution reached')
            pass
            return
        else:
            return abort(500, message="Internal Server Error")
    explain_result = cur.fetchall()
    print(f'Benchmark result, {explain_result[-2][0]}, {explain_result[-1][0]}')
    cur.close()

    diff_query = DIFF_QUERY_TEMPLATE.format(baseline_query, query, query, baseline_query)
    cur = benchmark_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute(diff_query)
    except (Exception, Error) as error:
        print(f'Benchmark diff query failed, error: {error}')
        return abort(500, message="Internal Server Error")
    result = cur.fetchall()[0][0]
    cur.close()
    correctness = 'Correct' if result == 'Same' else 'Incorrect'
    print(f'Benchmark query correctness: {correctness}')


class Submission(Resource):
    def get(self, submission_id):
        cur = submission_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        submission_id = f"'{submission_id}'"
        try:
            cur.execute(f'SELECT * FROM submission WHERE submission_id = {submission_id}')
        except (Exception, Error) as error:
            print(f'Submission query submission failed, error: {error}')
            return abort(400, message="Invalid Server Error")
        submission = cur.fetchone()
        cur.close()
        if submission is None:
            abort(404, message="Submission {} doesn't exist".format(submission_id))
        return {'user_name': submission['user_name'], 'query': submission['sql_query'], 'submission_id': submission_id,
                'timestamp': submission['created_at'].strftime("%m/%d/%Y, %H:%M:%S"),
                'challenge_id': submission['challenge_id'], 'planning_time': submission['planning_time'],
                'execution_time': submission['execution_time'], 'is_correct': submission['is_correct']}, 200

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
        challenge_cur = challenge_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        quoted_challenge_id = f"'{challenge_id}'"
        try:
            challenge_cur.execute(f'SELECT * FROM challenge WHERE challenge_id = {quoted_challenge_id}')
        except (Exception, Error) as error:
            print(f'Submission query challenge failed, error: {error}')
            return abort(500, message="Internal Server Error")
        challenge = challenge_cur.fetchone()
        challenge_cur.close()
        if not challenge:
            abort(404, message="Challenge {} doesn't exist".format(challenge_id))

        cur = submission_conn.cursor()
        dt = datetime.now(timezone.utc)
        submission_id = 'sub_' + str(uuid.uuid4())
        prepared_query = """ INSERT INTO submission (submission_id, user_name, created_at, updated_at, challenge_id, sql_query, execution_time, planning_time, is_correct) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        record = (submission_id, name, dt, dt, challenge_id, query, -1, -1, 'true')
        try:
            cur.execute(prepared_query, record)
        except (Exception, Error) as error:
            print(f'Submission insertion failed, error: {error}')
            return abort(500, message="Internal Server Error")
        submission_conn.commit()
        count = cur.rowcount
        print(f"{count} records inserted successfully into submission table")
        cur.close()
        benchmark_query(challenge['sql_query'], query)
        return {'user_name': name, 'query': query, 'submission_id': submission_id,
                'time_stamp': dt.strftime("%m/%d/%Y, %H:%M:%S"), 'challengeId': challenge_id, 'planning_time': -1,
                'execution_time': -1, 'is_correct': True}, 201


class Challenge(Resource):
    def get(self, challenge_id):
        cur = challenge_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        challenge_id = f"'{challenge_id}'"
        try:
            cur.execute(f'SELECT * FROM challenge WHERE challenge_id = {challenge_id}')
        except (Exception, Error):
            return abort(500, message="Internal Server Error")
        challenge = cur.fetchone()
        cur.close()
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
            return abort(400, message="Internal Query Syntax")
        name = args['user_name']
        cur = challenge_conn.cursor()
        dt = datetime.now(timezone.utc)
        challenge_id = 'ch_' + str(uuid.uuid4())
        prepared_query = """ INSERT INTO challenge (user_name, created_at, updated_at, challenge_id, sql_query) VALUES (%s, %s, %s, %s, %s)"""
        record = (name, dt, dt, challenge_id, query)
        try:
            cur.execute(prepared_query, record)
        except (Exception, Error) as error:
            print('Challenge insertion failed, error:', error)
            return abort(500, message="Internal Server Error")
        challenge_conn.commit()
        count = cur.rowcount
        print(f"{count} records inserted successfully into challenge table")
        cur.close()
        return {'user_name': name, 'query': query, 'challenge_id': challenge_id,
                'time_stamp': dt.strftime("%m/%d/%Y, %H:%M:%S")}, 201


api.add_resource(Submission, '/submissions', '/submissions/<submission_id>')
api.add_resource(Challenge, '/challenges', '/challenges/<challenge_id>')

if __name__ == '__main__':
    app.run(debug=True)
