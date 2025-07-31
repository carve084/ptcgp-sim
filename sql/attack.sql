DROP TABLE IF EXISTS attack CASCADE;
CREATE TABLE attack (
    id SERIAL PRIMARY KEY,
    cardId INT REFERENCES card(id),
    cost VARCHAR(255),
    name VARCHAR(255),
    effect TEXT,
    damage VARCHAR(255)
);