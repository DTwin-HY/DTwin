CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    prompt TEXT,
    reply TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(36) NOT NULL,
    item_id VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    amount NUMERIC(10,2)
);

