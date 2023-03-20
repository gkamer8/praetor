DROP TABLE IF EXISTS examples;
DROP TABLE IF EXISTS prompts;

CREATE TABLE examples (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tags TEXT,
  prompt_id INTEGER,
  elo INTEGER,
  subjective_score INTEGER,
  completion TEXT
);

CREATE TABLE prompts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tags TEXT,
  style TEXT,
  prompt TEXT
);

INSERT INTO examples (tags, prompt_id, elo, subjective_score, completion)
VALUES ("coding, Python, short",
        0,
        1500,
        10,
        "print('Hello World')"
        );

INSERT INTO prompts (tags, style, prompt)
VALUES ("coding, Python, simple, easy",
        "instruction",
        "Write a line of Python that prings 'Hello World'"
        );
