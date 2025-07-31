DROP TABLE IF EXISTS trophy CASCADE;
CREATE TABLE trophy (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    bronzeAmount INT,
    silverAmount INT,
    goldAmount INT,
    rainbowAmount INT,
    category VARCHAR(255)
);