DROP TABLE IF EXISTS card_type CASCADE;
CREATE TABLE card_type (
    cardId INT REFERENCES card(id),
    typeId INT REFERENCES type(id)
);