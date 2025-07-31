DROP TABLE IF EXISTS subtype CASCADE;
CREATE TABLE subtype (
    id INT PRIMARY KEY,
    name VARCHAR(255)
);

INSERT INTO subtype (id, name) VALUES
 (1, 'Fossil')
,(2, 'Item')
,(3, 'Supporter')
,(4, 'Tool')
,(5, 'Ultra Beast');

-- Expected future subtypes
--,("BREAK")
--,("Baby")
--,("GX")
--,("LEGEND")
--,("Level-Up")
--,("MEGA")
--,("Rapid Strike")
--,("Restored")
--,("Rocket's Secret Machine")
--,("Single Strike")
--,("Special")
--,("Stadium")
--,("TAG TEAM")
--,("Technical Machine")
--,("Tool F")
--,("V")
--,("VMAX");