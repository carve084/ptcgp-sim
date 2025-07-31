DROP TABLE IF EXISTS energy CASCADE;
CREATE TABLE energy (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    code CHAR
);

INSERT INTO energy (id, name, code) VALUES
  (1,   'Grass',        'G')
, (2,   'Fire',         'R')
, (3,   'Water',        'W')
, (4,   'Lightning',    'L')
, (5,   'Psychic',      'P')
, (6,   'Fighting',     'F')
, (7,   'Darkness',     'D')
, (8,   'Metal',        'M')
, (9,   'Dragon',       'A')
, (10,  'Colorless',    'C');