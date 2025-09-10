CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    prompt TEXT,
    reply TEXT
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
