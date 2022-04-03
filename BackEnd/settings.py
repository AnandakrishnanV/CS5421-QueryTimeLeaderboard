import os
import urllib.parse as urlparse

#DATABASE_URL: URL provided by online heroku postgres server
url = urlparse.urlparse(os.environ.get('DATABASE_URL'))
APP_DB_HOST=url.hostname
APP_DB_NAME=url.path[1:]
APP_DB_USER = url.username
APP_DB_PASSWORD = url.password

#HEROKU_POSTGRESQL_COBALT_URL: URL provided by online heroku postgres server
url_benchmark=urlparse.urlparse(os.environ.get('HEROKU_POSTGRESQL_COBALT_URL'))
BENCHMARK_DB_HOST=url_benchmark.hostname
BENCHMARK_DB_NAME=url_benchmark.path[1:]
BENCHMARK_DB_USER = url_benchmark.username
BENCHMARK_DB_PASSWORD = url_benchmark.password

#REDIS_URL: URL provided by online heroku postgres server
