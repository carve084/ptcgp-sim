DROP TABLE IF EXISTS ability CASCADE;
CREATE TABLE ability (
    id SERIAL PRIMARY KEY,
    cardId INT REFERENCES card(id),
    name VARCHAR(255),
    effect TEXT
);