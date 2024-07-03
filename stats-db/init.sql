CREATE SCHEMA IF NOT EXISTS stats_schema;
SET search_path TO stats_schema;

CREATE TABLE IF NOT EXISTS player_stats (
    Player VARCHAR(255) NOT NULL,
    Season VARCHAR(255) NOT NULL,
    Age int,
    Nationality VARCHAR(255),
    Team VARCHAR(255),
    Competition VARCHAR(255),
    MP int NOT NULL,
    Min int,
    "90s" FLOAT,
    Starts int,
    Subs int,
    unSub FLOAT,
    Goals int,
    Ast int,
    "G+A" int,
    Non_penalty_goals FLOAT,
    Penalties FLOAT,
    PK_attempted FLOAT,
    PK_missed FLOAT,
    Pos VARCHAR(255)
);
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM player_stats LIMIT 1) THEN
        COPY player_stats FROM '/docker-entrypoint-initdb.d/csv_data/players_formatted_int.csv' DELIMITER ',' CSV HEADER;
    END IF;
END $$;


DO $$
BEGIN
    DELETE FROM player_stats WHERE team = '2 Teams';
    COPY player_stats FROM '/docker-entrypoint-initdb.d/csv_data/two_teams_fixes.csv' DELIMITER ',' CSV HEADER;
END $$;

CREATE TABLE IF NOT EXISTS countries (
    country_code VARCHAR(3) NOT NULL,
    country VARCHAR(255) NOT NULL
);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM countries LIMIT 1) THEN
        COPY countries FROM '/docker-entrypoint-initdb.d/csv_data/countries.csv' DELIMITER ',' CSV HEADER;
    END IF;
END $$;

CREATE OR REPLACE VIEW player_goals_by_season_ranked as
	select 
		player,
		season,
		goals,
		ROW_NUMBER() OVER (PARTITION BY season ORDER BY goals DESC) AS rn
	from player_stats ps
	where goals is not null;

CREATE OR REPLACE VIEW goals_by_country_ranked as 
    select country, sum(goals) as total_goals
    from player_stats ps
    join countries c 
    on ps.nationality = c.country_code
    group by country
    having sum(goals) > 0
    order by total_goals desc;

create view goals_and_assists as
    select player, season, goals, ast 
    FROM stats_schema.player_stats
    order by player, season;


