
CREATE TABLE IF NOT EXISTS posts (
    id integer PRIMARY KEY AUTOINCREMENT,
    authour text NOT NULL,
    title TEXT NOT NULL,
    content text NOT NULL,
    authour_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id integer PRIMARY KEY AUTOINCREMENT,
    name_ text NOT NULL UNIQUE,
    pass TEXT NOT NULL
);
