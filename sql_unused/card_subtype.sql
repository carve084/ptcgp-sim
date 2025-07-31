DROP TABLE IF EXISTS card_subtype CASCADE;
CREATE TABLE card_subtype (
    cardId INT REFERENCES card(id),
    subtypeId INT REFERENCES subtype(id)
);