DROP TABLE IF EXISTS "set" CASCADE;
CREATE TABLE "set" (
    id SERIAL PRIMARY KEY,
    code VARCHAR(255),
    name VARCHAR(255),
    cardCountOfficial INT,
    cardCountTotal INT,
    logo VARCHAR(255),
    symbol VARCHAR(255)
);