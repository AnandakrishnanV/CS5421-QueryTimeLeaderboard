CREATE TABLE submission (
  challenge_id varchar NOT NULL,
  submission_id varchar PRIMARY KEY,
  user_name varchar NOT NULL,
  created_at timestamp DEFAULT current_timestamp(),
  updated_at timestamp DEFAULT current_timestamp(),
  sql_query TEXT,
  execution_time decimal NOT NULL DEFAULT 0,
  planning_time decimal NOT NULL DEFAULT 0,
  total_time decimal NOT NULL DEFAULT 0,
  is_correct boolean NOT NULL DEFAULT FALSE,
  error_message varchar NOT NULL DEFAULT '',
  retry_times int DEFAULT 0,
  CONSTRAINT fk_challenge
      FOREIGN KEY(challenge_id)
	  REFERENCES challenge(challenge_id)
  CONSTRAINT fk_username
      FOREIGN KEY(user_name)
	  REFERENCES users(user_name)
);

CREATE TABLE challenge (
  challenge_id varchar PRIMARY KEY,
  user_name varchar NOT NULL,
  challenge_name varchar NOT NULL,
  challenge_type smallint NOT NULL,
  created_at timestamp DEFAULT current_timestamp(),
  updated_at timestamp DEFAULT current_timestamp(),
  sql_query TEXT,
  description TEXT,
  CONSTRAINT fk_challenge_type
      FOREIGN KEY(challenge_type)
	  REFERENCES challenge_type(challenge_type)
  CONSTRAINT fk_username
      FOREIGN KEY(user_name)
	  REFERENCES users(user_name)
);

CREATE TABLE challenge_type (
    challenge_type smallint PRIMARY KEY,
    description varchar NOT NULL DEFAULT '',
    user_name varchar NOT NULL DEFAULT '',
    created_at timestamp DEFAULT current_timestamp(),
    updated_at timestamp DEFAULT current_timestamp(),
    CONSTRAINT fk_username
      FOREIGN KEY(user_name)
	  REFERENCES users(user_name)
);

CREATE TABLE users (
    user_name varchar PRIMARY KEY,
    password varchar NOT NULL,
    is_admin boolean NOT NULL DEFAULT FALSE,
    created_at timestamp DEFAULT current_timestamp(),
    updated_at timestamp DEFAULT current_timestamp(),
);

-- insert challenge types, can be done offline
INSERT INTO challenge_type(challenge_type, description, user_name, created_at, updated_at)
VALUES
(1, 'Slowest Query', 'professor', current_timestamp(), current_timestamp()),
(2, 'Fastest Query', 'teaching assistant', current_timestamp(), current_timestamp());


-- insert users with hashed passwords offline
-- all password hashes are generated from the password "jw8s0F4"
INSERT INTO users(user_name, password, is_admin)
VALUES
('stu1','sha256$IAhWnnEuSEUX6jTf$f27a7e6d15b48f53350e02c0600aec3254837a9484f8f3d439059d21ac3d1b30','False',current_timestamp(), current_timestamp()),
('professor','sha256$IAhWnnEuSEUX6jTf$f27a7e6d15b48f53350e02c0600aec3254837a9484f8f3d439059d21ac3d1b30','True'),
('teaching assistant','sha256$IAhWnnEuSEUX6jTf$f27a7e6d15b48f53350e02c0600aec3254837a9484f8f3d439059d21ac3d1b30','True',current_timestamp(), current_timestamp())

-- grant all permission to a user
GRANT ALL
ON submission
TO test;

-- grant only select permission to a user
GRANT SELECT
ON benchmark
TO test;