DROP TABLE IF EXISTS supertype CASCADE;
CREATE TABLE supertype (
    id INT PRIMARY KEY,
    name VARCHAR(255)
);

INSERT INTO supertype (id, name) VALUES
(1, 'Pokemon')
, (2, 'Trainer');