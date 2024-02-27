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
        COPY player_stats FROM '/docker-entrypoint-initdb.d/csv_data/players.csv' DELIMITER ',' CSV HEADER;
    END IF;
END $$;

CREATE OR REPLACE VIEW player_goals_by_season_ranked as
	select 
		player,
		season,
		goals,
		ROW_NUMBER() OVER (PARTITION BY season ORDER BY goals DESC) AS rn
	from player_stats ps
	where season != '2023-2024' and goals is not null;

CREATE OR REPLACE VIEW goals_by_country_ranked as 
	select nationality, sum(goals) as total_goals
	from player_stats ps
	where season != '2023-2024'
	group by nationality
	having sum(goals) > 0
	order by total_goals desc;


