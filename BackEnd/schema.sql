CREATE TABLE submission (
  challenge_id varchar NOT NULL,
  submission_id varchar PRIMARY KEY,
  user_name varchar NOT NULL,
  created_at timestamp,
  updated_at timestamp,
  sql_query TEXT,
  execution_time decimal NOT NULL DEFAULT 0,
  planning_time decimal NOT NULL DEFAULT 0,
  is_correct boolean NOT NULL DEFAULT FALSE,
  error_message varchar NOT NULL DEFAULT '',
  retry_times int DEFAULT 0,
  CONSTRAINT fk_challenge
      FOREIGN KEY(challenge_id)
	  REFERENCES challenge(challenge_id)
);

CREATE TABLE challenge (
  challenge_id varchar PRIMARY KEY,
  user_name varchar NOT NULL,
  challenge_name varchar NOT NULL,
  challenge_type smallint NOT NULL,
  created_at timestamp,
  updated_at timestamp,
  sql_query TEXT,
  description TEXT,
  CONSTRAINT fk_challenge_type
      FOREIGN KEY(challenge_type)
	  REFERENCES challenge_type(challenge_type)
);

CREATE TABLE challenge_type (
    challenge_type smallint PRIMARY KEY,
    description varchar NOT NULL DEFAULT '',
    user_name varchar NOT NULL DEFAULT '',
    created_at timestamp,
    updated_at timestamp,
);

-- insert challenge types, can be done offline
INSERT INTO challenge_type(challenge_type, description, user_name, created_at, updated_at)
VALUES
(1, 'Slowest Query', 'professor', current_timestamp(), current_timestamp()),
(2, 'Fastest Query', 'teaching assistant', current_timestamp(), current_timestamp());

-- grant all permission to a user
GRANT ALL
ON submission
TO test;

-- grant only select permission to a user
GRANT SELECT
ON benchmark
TO test;