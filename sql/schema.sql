CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    info TEXT NOT NULL,
    done INTEGER DEFAULT 0
);