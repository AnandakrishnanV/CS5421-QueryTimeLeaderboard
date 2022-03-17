CREATE TABLE submission (
  challenge_id VARCHAR NOT NULL,
  submission_id VARCHAR PRIMARY KEY,
  user_name VARCHAR NOT NULL,
  created_at timestamp ,
  updated_at timestamp ,
  sql_query TEXT,
  execution_time int,
  planning_time int,
  is_correct boolean,
  CONSTRAINT fk_challenge
      FOREIGN KEY(challenge_id)
	  REFERENCES challenge(challenge_id)
);

CREATE TABLE challenge (
  challenge_id VARCHAR PRIMARY KEY,
  user_name VARCHAR NOT NULL,
  created_at timestamp ,
  updated_at timestamp ,
  sql_query TEXT
);