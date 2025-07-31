DROP TABLE IF EXISTS rarity CASCADE;
CREATE TABLE rarity (
    id INT PRIMARY KEY,
    symbol VARCHAR(255),
    name VARCHAR(255),
    dotggName VARCHAR(255),
    code VARCHAR(255)
);

INSERT INTO rarity (id, symbol, name, dotggName, code) VALUES
  (1,   '◊',    'One Diamond',      'Common',           'C')
, (2,   '◊◊',   'Two Diamond',      'Uncommon',         'U')
, (3,   '◊◊◊',  'Three Diamond',    'Rare',             'R')
, (4,   '◊◊◊◊', 'Four Diamond',     'Double Rare',      'RR')
, (5,   '☆',    'One Star',         'Art Rare',         'AR')
, (6,   '☆☆',   'Two Star',         'Super Rare',       'SR')
, (7,   '☆☆',   'Two Star',         'Special Art Rare', 'SAR')
, (8,   '☆☆☆',  'Three Star',       'Immersive Rare',   'IM')
, (9,   '♕',    'Crown',            'Crown Rare',       'UR')
, (10,  '✵',    'One Shiny',        'Shiny',            'S')
, (11,  '✵✵',   'Two Shiny',        'Shiny Super Rare', 'SSR');