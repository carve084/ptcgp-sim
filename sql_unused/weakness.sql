DROP TABLE IF EXISTS weakness CASCADE;
CREATE TABLE weakness (
    id SERIAL PRIMARY KEY,
    cardId INT REFERENCES card(id),
    typeId INT REFERENCES type(id),
    "value" INT
);