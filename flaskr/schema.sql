DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS tasks;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  deadline TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT,
  finished BIT,
  filename TEXT,
  filedata BLOB,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
