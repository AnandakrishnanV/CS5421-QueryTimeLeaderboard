import psycopg2
from psycopg2 import Error
import psycopg2.extras
import sqlvalidator


def get_db_connection(host: str, database: str, user: str, password: str, timeout: int = 5000,
                      readonly: bool = False, autocommit: bool = True):
    options = f'-c statement_timeout={timeout}'
    conn = psycopg2.connect(host=host,
                            database=database,
                            user=user,
                            password=password, options=options)
    conn.set_session(readonly=readonly, autocommit=autocommit)
    return conn


def execute_query(db_conn, query, **kwargs):
    cur = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        if kwargs.get('values'):
            cur.execute(query, kwargs.get('values'))
        else:
            cur.execute(query)
    except (Exception, Error) as error:
        cur.close()
        db_conn.close()
        raise error
    return cur

def validate_sql_syntax(query: str):
    sql_query = sqlvalidator.parse(query)
    if not sql_query.is_valid():
        print(f'invalid query: {query}, errors: {sql_query.errors}')
        return False
    return True

