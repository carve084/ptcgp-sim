DROP TABLE IF EXISTS route CASCADE;
CREATE TABLE route (
    id SERIAL PRIMARY KEY,
    routeAFlairs INT[],
    routeBFlairs INT[],
    routeCFlairs INT[]
);