import psycopg2


def get_db_connection(host: str, database: str, user: str, password: str, timeout: int = 5000,
                      readonly: bool = False, autocommit: bool = True):
    options = f'-c statement_timeout={timeout}'
    conn = psycopg2.connect(host=host,
                            database=database,
                            user=user,
                            password=password, options=options)
    conn.set_session(readonly=readonly, autocommit=autocommit)
    return conn
