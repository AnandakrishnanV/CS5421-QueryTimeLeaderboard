#!/bin/bash

# either copy this export command below and run in the same shell instance where the application will be run or
# execute the script using `. set_env.sh`
# note that this is just a sample bash script to set the necessary env variables before running the app
# the respective values should be replaced with those pertaining to the actual deployment environment
export REDIS_URL='redis://localhost:6379' REDIS_URL='redis://localhost:6379' \
  SECRET_KEY='8454e5a14e6c4a3490e85f8cd0737fa0' APP_DB_HOST='localhost' \
  APP_DB_PORT=5432 APP_DB_NAME='tuning' APP_DB_USER='test' APP_DB_PASSWORD='test' \
  BENCHMARK_DB_HOST='localhost' BENCHMARK_DB_NAME='tuning' BENCHMARK_DB_PORT=5432 BENCHMARK_DB_USER='read_user' \
  BENCHMARK_DB_PASSWORD='read_user' BENCHMARK_DB_NAME='tuning' BENCHMARK_TIMEOUT=5000 \
  JWT_CONFIG='POST_ONLY' JWT_VALIDITY_PERIOD=30 BENCHMARK_ROUNDS=10
