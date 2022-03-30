from abc import ABC

import celery
from db_client import get_db_connection
from db_client import execute_query
from datetime import datetime, timezone
from psycopg2 import ProgrammingError
from psycopg2.errors import ReadOnlySqlTransaction, IntegrityError, InvalidTextRepresentation


class BenchMarkTask(celery.Task, ABC):

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        # exc (Exception) - The exception raised by the task.
        # args (Tuple) - Original arguments for the task that failed.
        # kwargs (Dict) - Original keyword arguments for the task that failed.
        try:
            count = self.helper(exc, kwargs)
            print(f"{count} records successfully updated for submission table on benchmarking timeout on retry, task id: {task_id}")
        except (Exception, Error) as error:
            print(f'Update benchmark result failed on retry, error: {error}, task id: {task_id}')

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # exc (Exception) - The exception raised by the task.
        # args (Tuple) - Original arguments for the task that failed.
        # kwargs (Dict) - Original keyword arguments for the task that failed.
        try:
            count = self.helper(exc, kwargs)
            print(f"{count} records successfully updated for submission table on benchmarking timeout on failure, task id: {task_id}")
        except (Exception, Error) as error:
            print(f'Update benchmark result failed on failure, error: {error}, task id: {task_id}')

    def helper(self, exc, kwargs):
        dt = datetime.now(timezone.utc)
        conn = get_db_connection(host='localhost', database='tuning', user='test', password='test')
        error_message = str(exc)
        cur = execute_query(db_conn=conn,
                            query=f"UPDATE submission SET updated_at = '{dt}', error_message = '{error_message}', retry_times = retry_times + 1 WHERE submission_id = '{kwargs.get('submission_id')}'")
        count = cur.rowcount
        cur.close()
        conn.close()
        return count


def process_error(e):
    if isinstance(e, ProgrammingError) or isinstance(e, ReadOnlySqlTransaction) or \
            isinstance(e, IntegrityError) or isinstance(e, InvalidTextRepresentation):
        return NonRetryableError(e)
    else:
        return RetryableError(e)


class Error(Exception):
    pass


class RetryableError(Error):
    pass


class NonRetryableError(Error):
    pass
