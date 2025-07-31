DROP TABLE IF EXISTS demand CASCADE;
CREATE TABLE demand (
    id SERIAL PRIMARY KEY,
    flairId INT REFERENCES flair(id),
    name VARCHAR(255),
    slug VARCHAR(255),
    image VARCHAR(2083),
    amount INT
);