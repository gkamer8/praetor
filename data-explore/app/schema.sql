DROP TABLE IF EXISTS examples;
DROP TABLE IF EXISTS prompts;
DROP TABLE IF EXISTS metrics;

CREATE TABLE examples (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `tags` TEXT,
  `prompt_id` INTEGER,
  `completion` TEXT
);

CREATE TABLE prompts (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `tags` TEXT,
  `style` TEXT,
  `prompt` TEXT
);

CREATE TABLE metrics (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` TEXT,
  `score` TEXT,
  `example_id` INTEGER
);

INSERT INTO examples (tags, prompt_id, completion)
VALUES ("coding, Python, short",
        1,
        "print('Hello World')"
        );

INSERT INTO prompts (tags, style, prompt)
VALUES ("coding, Python, simple, easy",
        "instruct",
        "Write a line of Python that prints 'Hello World'"
        );

INSERT INTO metrics (`name`, `score`, `example_id`)
VALUES ("elo",
        1500,
        1
        );
