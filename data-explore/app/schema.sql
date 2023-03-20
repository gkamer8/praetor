DROP TABLE IF EXISTS examples;
DROP TABLE IF EXISTS prompts;

CREATE TABLE examples (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tags TEXT,
  prompt_id INTEGER,
  completion TEXT
);

CREATE TABLE prompts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tags TEXT,
  style TEXT,
  prompt TEXT
);
