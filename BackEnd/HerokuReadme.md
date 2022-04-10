# Heroku deployment steps

## Setup
1. Create a new `Heroku` app 
2. Setup online PostgreSQL: Set up two independent Heroku postgreSQL database servers as application and benchmark respectively. \
   `heroku resource page -> add-ons -> select 'Heroku Postgres'. Repeat the step for 2 times`
    
3. Check config variables for postgreSQL: Update the local environment variables to the generated for postgreSQL variables. Code template is in `settings.py`\
`heroku settings page -> reveal config vars -> copy DATABASE_URL & HEROKU_POSTGRESQL_<COLOR>_URL as the keyword and assign to enviroment -> parse the URL to APP_DB_HOST,APP_DB_NAME,APP_DB_USER, APP_DB_PASSWORD & BENCHMARK_DB_HOST, BENCHMARK_DB_NAME, BENCHMARK_DB_USER, BENCHMARK_DB_PASSWORD.`

4. Create a set of users with appropriate privileges as needed. Be cautious with the foreign key constraints. The hased password generation is \
`from werkzeug.security import generate_password_hash       
   hashed_password=generate_password_hash(<password str>, method='sha256')`
5. Set up setting files for Heroku: Heroku required miscellanous files to run on cloud. Files include `runtime.txt`, `Procfile`. If environment variables are involved `settings.py` is needed as well. The files contain python version, library requirements, app running command (both app and celery) and URL parser. Sample files can be found in this directory. 
6. Insert database `schema.sql` by `psql` command line to the online databases.\
link to database: `psql postgres://frviimjercuozi:4ff7da9eb9a7646aec1da98aa9ae908ef5ab19c5b4191d6b805ea0eb8fa8088e@ec2-54-173-77-184.compute-1.amazonaws.com:5432/d102e5d549lrbe -f schema.sql`\
   execute .sql file: `heroku pg:psql --app cs5421prj-backend <initialize.sql  `
   
7. Set up online Redis: Set up Heroku Redis for asynchronous benchmark activity. \
`heroku resource page -> add-ons -> select 'Heroku Redis'.`
   
8. Check config variables for Redis: Update the local environment variables to the generated for Redis variables. Code template is in `settings.py`\
`heroku settings page -> reveal config vars -> copy REDIS_URL as the keyword and assign to enviroment.`     
   
9. Update `config vars` on Heroku: Add all environment variables on heroku to make the app working. \
`heroku settings page -> reveal config vars -> Add key & value`


## Routes & Testing
### Challenge API
### Challenge Type API
#### Create a Challenge Type
**POST \challenge_types** \
`curl -X POST -H "Content-Type: application/json" \
    -d '{"challenge_type": 3, "description": "correct query", "user_name": "ta"}' \
    http://cs5421prj-backend.herokuapp.com//challenge_types`
#### Retrieve a List of Challenge Types
**GET \challenge_types** \
`curl -X GET http://cs5421prj-backend.herokuapp.com/challenge_types`
#### Retrieve a Challenge Type
**GET \challenge_type\\<challenge_type>** \
`curl -X GET http://cs5421prj-backend.herokuapp.com/challenge_type/1`
#### Create a Challenge
**POST \challenges** \
`curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "select * from test;", "user_name": "test", "challenge_name": "challenge 1", "challenge_type": 1, "challenge_description": "test challenge"}' \
    http://cs5421prj-backend.herokuapp.com/challenges`
#### Retrieve a List of Challenges
**GET \challenges** \
`curl -X GET http://cs5421prj-backend.herokuapp.com/challenges` \
`curl -X GET http://cs5421prj-backend.herokuapp.com/challenges?user_name=xxx`
#### Retrieve a Challenge
**GET \challenge\\<challenge_id>** \
`curl -X GET http://cs5421prj-backend.herokuapp.com/challenge/ch_xxx`
#### Delete a Challenge
`curl -X DELETE http://cs5421prj-backend.herokuapp.com/challenge/ch_xxx`
### Submission API
#### Create a Submission
**POST \submissions** \
`curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "select * from benchmarking;", "challenge_id": "ch_xxx", "user_name": "test"}' \
    http://cs5421prj-backend.herokuapp.com/submissions`
#### Retrieve a List of Submissions
**GET \submissions** \
`curl -X GET http://cs5421prj-backend.herokuapp.com/submissions` \
`curl -X GET http://cs5421prj-backend.herokuapp.com/submissions?user_name=xxx`
`curl -X GET http://cs5421prj-backend.herokuapp.com/submissions?challenge_id=ch_xxx`
`curl -X GET http://cs5421prj-backend.herokuapp.com/submissions?user_name=xxx&challenge_id=ch_xxx`
#### Retrieve a Submission
**GET \submission\\<submission_id>** \
`curl -X GET http://cs5421prj-backend.herokuapp.com/submission/sub_xxx`

#### Log in with user_name and password
`curl -X POST -H "Content-Type: application/json" -d '{"user_name": <username>, "password": <password>}' http://cs5421prj-backend.herokuapp.com/login`

## Authentication
The web application is invitation based so no sign up mechanism is provided as of now. Intended users will be given their login credentials in a secured manner.
Login is required for API access as specified by the environment variable `JWT_CONFIG`. Two modes are currently supported, namely `ALL`, `POST_ONLY`, `DISABLED`. Note that resource mutating requests including `PUT`, `DELETE` are also regarded as `POST` requests. Upon successful login, a JSON Web Token with 30 minutes of validity period will be returned. Subsequent requests must carry the same JWT in request headers named `TOKEN`. Meanwhile, `USER` must be set for all request headers for cross validation.
### Examples
`curl -X POST -H "Content-Type: application/json" -H "TOKEN: xxx" -H "USER: xxx"\
    -d '{"query": "select * from items", "challenge_id": "ch_3865812a-906f-46bd-8ff6-6e76e48cec6f", "user_name": "test"}' \
    http://cs5421prj-backend.herokuapp.com/submissions?token=xxx` \
`curl -X DELETE -H "TOKEN: xxx" -H "USER: xxx" http://cs5421prj-backend.herokuapp.com/challenge/ch_xxx` \
`curl -X GET -H "TOKEN: xxx" -H "USER: xxx" http://cs5421prj-backend.herokuapp.com/submissions`



