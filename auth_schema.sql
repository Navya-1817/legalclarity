-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Add user_id to documents table
ALTER TABLE documents ADD COLUMN user_id INTEGER REFERENCES users(id);
