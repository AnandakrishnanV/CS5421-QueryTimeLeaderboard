# Python Backend with Heroku integration

## Setup
1. Set up and run two independent `PostgreSQL` server instances, one for application data and the other one for running benchmarking. Set up the two databases according to `schema.sql` and create a set of users with appropriate privileges as needed. Be cautious with the foreign key constraints.
2. Set up and run a Redis instance as task queue broker. If you are using docker, simply do `docker run \
    -e ALLOW_EMPTY_PASSWORD=yes -p 6379:6379 \
    -v /usr/redis:/bitnami/redis/data \
    bitnami/redis:latest`.
3. Set up the main project by installing the dependencies listed in `requirements.txt` using `pip3`.
4. `cd` into the BackEnd directory abd run the project using `python3 app.py`.
5. Open another terminal tab and start the celery task queue worker using `celery -A app.celery worker --loglevel=INFO --concurrency 1 -P solo`. The `-P solo` option is given as a workaround to run celery properly on Windows. Drop it when running on Linux based machines.
6. Open one more terminal tab and start the celery monitor agent using `celery -A app.celery flower`.

## Routes & Testing
### Challenge API
### Challenge Type API
#### Create a Challenge Type
**POST \challenge_types** \
`curl -X POST -H "Content-Type: application/json" \
    -d '{"challenge_type": 3, "description": "correct query", "user_name": "ta"}' \
    http://127.0.0.1:5000/challenge_types`
#### Retrieve a List of Challenge Types
**GET \challenge_types** \
`curl http://127.0.0.1:5000/challenge_types`
#### Retrieve a Challenge Type
**GET \challenge_type\\<challenge_type>** \
`curl http://127.0.0.1:5000/challenge_type/1`
#### Create a Challenge
**POST \challenges** \
`curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "select * from test;", "user_name": "test", "challenge_name": "challenge 1", "challenge_type": 1, "challenge_description": "test challenge"}' \
    http://127.0.0.1:5000/challenges`
#### Retrieve a List of Challenges
**GET \challenges** \
`curl http://127.0.0.1:5000/challenges` \
`curl http://127.0.0.1:5000/challenges?user_name=xxx`
#### Retrieve a Challenge
**GET \challenge\\<challenge_id>** \
`curl http://127.0.0.1:5000/challenge/ch_xxx`
### Submission API
#### Create a Submission
**POST \submissions** \
`curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "select * from benchmarking;", "challenge_id": "ch_xxx", "user_name": "test"}' \
    http://127.0.0.1:5000/submissions`
#### Retrieve a List of Submissions
**GET \submissions** \
`curl http://127.0.0.1:5000/submissions` \
`curl http://127.0.0.1:5000/submissions?user_name=xxx`
`curl http://127.0.0.1:5000/submissions?challenge_id=ch_xxx`
`curl http://127.0.0.1:5000/submissions?user_name=xxx&challenge_id=ch_xxx`
#### Retrieve a Submission
**GET \submission\\<submission_id>** \
`curl http://127.0.0.1:5000/submission/sub_xxx`

#### Log in with user_name and password
`curl -X POST -H "Content-Type: application/json" -d '{"user_name": <username>, "password": <password>}' http://127.0.0.1:5000/login`

## Authentication
The web application is invitation based so no sign up mechanism is provided as of now. Intended users will be given their login credentials in a secured manner.
Login is required for access to all APIs. Upon successful login, a JSON Web Token with 30 minutes of validity period will be returned. Subsequent requests must carry the same JWT in request headers named `TOKEN`. Meanwhile, `USER` must be set for all request headers for cross validation.
### Examples
`curl -X POST -H "Content-Type: application/json" -H "TOKEN: xxx" -H "USER: xxx"\
    -d '{"query": "select * from items", "challenge_id": "ch_3865812a-906f-46bd-8ff6-6e76e48cec6f", "user_name": "test"}' \
    http://127.0.0.1:5000/submissions?token=xxx` \
`curl -H "TOKEN: xxx" -H "USER: xxx" http://127.0.0.1:5000/submissions`



