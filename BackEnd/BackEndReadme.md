# Python Backend with Heroku integration

## Setup
1. Set up and run two independent `PostgreSQL` server instances, one for application data and the other one for running benchmarking. Set up the two databases according to `schema.sql` and create a set of users with appropriate privileges as needed.
2. Set up and run a Redis instance as task queue broker. If you are using docker, simply do `docker run \
    -e ALLOW_EMPTY_PASSWORD=yes -p 6379:6379 \
    -v /usr/redis:/bitnami/redis/data \
    bitnami/redis:latest`.
3. Set up the main project by installing the dependencies listed in `requirements.txt` using `pip3`.
4. `cd` into the BackEnd directory abd run the project using `python3 app.py`.
5. Open another terminal tab and start the celery task queue worker using `celery -A app.celery worker --loglevel=INFO --concurrency 1 -P solo`. The `-P solo` option is given as a workaround to run celery properly on Windows. Drop it when running on Linux based machines.
6. Open one more terminal tab and start the celery monitor agent using `celery -A app.celery flower`.

## Routes & Testing
### Create a Challenge
**POST \challenges** \
`curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "select * from test;", "user_name": "test"}' \
    http://127.0.0.1:5000/challenges`
### Retrieve a Challenge
**GET \challenge\<challenge_id>** \
`curl http://127.0.0.1:5000/challenge/ch_xxx`
### Retrieve a List of Challenges
**GET \challenges** \
`curl http://127.0.0.1:5000/challenges`
### Create a Submission
**POST \submissions** \
`curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "select * from benchmarking;", "challenge_id": "ch_xxx", "user_name": "test"}' \
    http://127.0.0.1:5000/submissions`
### Retrieve a Submission
**GET \submissions\<submission_id>** \
`curl http://127.0.0.1:5000/submission/sub_xxx`
### Retrieve a List of Submissions
**GET \submissions\<submission_id>** \
`curl http://127.0.0.1:5000/submissions` \
`curl http://127.0.0.1:5000/submissions?user_name=xxx`
