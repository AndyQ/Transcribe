DROP TABLE IF EXISTS waiting;


CREATE TABLE item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    file_name TEXT NOT NULL,
    source_url TEXT,
    transcription_file TEXT,
    status TEXT NOT NULL,
    error_reason TEXT,
    status_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


