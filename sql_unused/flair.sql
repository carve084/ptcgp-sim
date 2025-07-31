DROP TABLE IF EXISTS flair CASCADE;
CREATE TABLE flair (
    id SERIAL PRIMARY KEY,
    type VARCHAR(255),
    name VARCHAR(255),
    image VARCHAR(2083),
    description TEXT
);