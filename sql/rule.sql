DROP TABLE IF EXISTS rule CASCADE;
CREATE TABLE rule (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL
);

INSERT INTO rule (id, name, description) VALUES
(1, 'ex', 'When your Pokémon ex is Knocked Out, your opponent gets 2 points.'),
(2, 'Item', 'You may play any number of Item cards during your turn.'),
(3, 'Supporter', 'You may play only 1 Supporter card during your turn.'),
(4, 'Tool', 'You use Pokémon Tools by attaching them to your Pokémon. You may attach only 1 Pokémon Tool to each Pokémon, and it stays attached.');