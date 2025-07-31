DROP TABLE IF EXISTS card_booster CASCADE;
CREATE TABLE card_booster (
    cardId INT REFERENCES card(id),
    boosterId INT REFERENCES booster(id)
);