DROP TABLE IF EXISTS booster CASCADE;
CREATE TABLE booster (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    code VARCHAR(255),
    dotggCode VARCHAR(255),
    setId INT REFERENCES set(id)
);