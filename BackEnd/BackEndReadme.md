# Python Backend with Heroku integration

## Setup
1. Set up and run two independent `PostgreSQL` server instances, one for application data and the other one for running benchmarking. Set up the two databases according to `schema.sql` and create a set of users with appropriate privileges as needed. Be cautious with the foreign key constraints.
2. Set up and run a Redis instance as task queue broker. If you are using docker, simply do `docker run \
    -e ALLOW_EMPTY_PASSWORD=yes -p 6379:6379 \
    -v /usr/redis:/bitnami/redis/data \
    bitnami/redis:latest`.
3. Set up the main project by installing the dependencies listed in `requirements.txt` using `pip3`.
4. Set up the required environment variables securely according the example given in set_up.sh. Replace the sample values with the actual application credentials. Note that the bash script is only given as a sample and its contents should not be stored on the server which could lead to potential security breach. Either copy the export command and run in the same bash shell where the application will be served or simply execute `. set_env.sh`.
5. In the same shell instance, run the project by executing `python3 app.py`.
6. Open another terminal tab, in the same shell, execute the same `set_env.sh` and then start the celery task queue worker using `celery -A app.celery worker --loglevel=INFO --concurrency 1 -P solo`. The `-P solo` option is given as a workaround to run celery properly on Windows. Drop it when running on Linux based machines.
7. Open one more terminal tab and start the celery monitor agent using `celery -A app.celery flower`.

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
`curl -X GET http://127.0.0.1:5000/challenge_types`
#### Retrieve a Challenge Type
**GET \challenge_type\\<challenge_type>** \
`curl -X GET http://127.0.0.1:5000/challenge_type/1`
#### Create a Challenge
**POST \challenges** \
`curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "select * from test;", "user_name": "test", "challenge_name": "challenge 1", "challenge_type": 1, "challenge_description": "test challenge"}' \
    http://127.0.0.1:5000/challenges`
#### Retrieve a List of Challenges
**GET \challenges** \
`curl -X GET http://127.0.0.1:5000/challenges` \
`curl -X GET http://127.0.0.1:5000/challenges?user_name=xxx`
#### Retrieve a Challenge
**GET \challenge\\<challenge_id>** \
`curl -X GET http://127.0.0.1:5000/challenge/ch_xxx`
### Submission API
#### Create a Submission
**POST \submissions** \
`curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "select * from benchmarking;", "challenge_id": "ch_xxx", "user_name": "test"}' \
    http://127.0.0.1:5000/submissions`
#### Retrieve a List of Submissions
**GET \submissions** \
`curl -X GET http://127.0.0.1:5000/submissions` \
`curl -X GET http://127.0.0.1:5000/submissions?user_name=xxx`
`curl -X GET http://127.0.0.1:5000/submissions?challenge_id=ch_xxx`
`curl -X GET http://127.0.0.1:5000/submissions?user_name=xxx&challenge_id=ch_xxx`
#### Retrieve a Submission
**GET \submission\\<submission_id>** \
`curl -X GET http://127.0.0.1:5000/submission/sub_xxx`

#### Log in with user_name and password
`curl -X POST -H "Content-Type: application/json" -d '{"user_name": <username>, "password": <password>}' http://127.0.0.1:5000/login`

## Authentication
The web application is invitation based so no sign up mechanism is provided as of now. Intended users will be given their login credentials in a secured manner.
Login is required for API access as specified by the environment variable `JWT_CONFIG`. Two modes are currently supported, namely `ALL`, `POST_ONLY`. Upon successful login, a JSON Web Token with 30 minutes of validity period will be returned. Subsequent requests must carry the same JWT in request headers named `TOKEN`. Meanwhile, `USER` must be set for all request headers for cross validation.
### Examples
`curl -X POST -H "Content-Type: application/json" -H "TOKEN: xxx" -H "USER: xxx"\
    -d '{"query": "select * from items", "challenge_id": "ch_3865812a-906f-46bd-8ff6-6e76e48cec6f", "user_name": "test"}' \
    http://127.0.0.1:5000/submissions?token=xxx` \
`curl -X GET -H "TOKEN: xxx" -H "USER: xxx" http://127.0.0.1:5000/submissions`



