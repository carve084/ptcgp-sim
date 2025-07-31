DROP TABLE IF EXISTS card CASCADE;
CREATE TABLE card (
    id SERIAL PRIMARY KEY,
    code VARCHAR(255),
    setId INT REFERENCES "set"(id),
    localId INT,
    name VARCHAR(255),
    supertypeId INT REFERENCES supertype(id),
    illustrator VARCHAR(255),
    image VARCHAR(2083),
    rarityId INT REFERENCES rarity(id),
    hp INT,
    energyTypeId INT REFERENCES energy(id),
    evolveFromName VARCHAR(255),
    text TEXT,
    stage VARCHAR(255),
    weaknessId INT REFERENCES energy(id),
    retreatCost INT,
    subtypeId INT REFERENCES subtype(id),
    ruleId INT REFERENCES rule(id)
);

-- Expected future columns
-- limited BOOLEAN DEFAULT FALSE, -- ACE SPEC or Radiant cards limited to 1 per deck