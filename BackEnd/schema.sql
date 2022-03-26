CREATE TABLE submission (
  challenge_id VARCHAR NOT NULL,
  submission_id VARCHAR PRIMARY KEY,
  user_name VARCHAR NOT NULL,
  created_at timestamp,
  updated_at timestamp,
  sql_query TEXT,
  execution_time int NOT NULL DEFAULT 0,
  planning_time int NOT NULL DEFAULT 0,
  is_correct boolean NOT NULL DEFAULT FALSE,
  error_message VARCHAR NOT NULL DEFAULT '',
  retry_times int DEFAULT 0,
  CONSTRAINT fk_challenge
      FOREIGN KEY(challenge_id)
	  REFERENCES challenge(challenge_id)
);

CREATE TABLE challenge (
  challenge_id VARCHAR PRIMARY KEY,
  user_name VARCHAR NOT NULL,
  created_at timestamp,
  updated_at timestamp,
  sql_query TEXT
);

-- grant all permission to a user
GRANT ALL
ON submission
TO test;

-- grant only select permission to a user
GRANT SELECT
ON benchmark
TO test;