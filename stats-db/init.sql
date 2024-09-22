CREATE SCHEMA IF NOT EXISTS stats_schema;
SET search_path TO stats_schema;

CREATE TABLE IF NOT EXISTS countries (
    country_code VARCHAR(3) NOT NULL,
    country VARCHAR(255) NOT NULL,
    primary key(country_code, country)
);

create table if not exists players (
	player_id integer primary key,
	player_name varchar(255) not null,
	nationality varchar(255)
);

CREATE TABLE IF NOT EXISTS leagues (
    league_id integer primary key,
    league_name varchar(255) not null
);

CREATE TABLE IF NOT EXISTS season_stats (
	stats_id SERIAL primary key,
	player_id integer references players (player_id),
    season varchar(255),
	"age" int,
    team VARCHAR(255),
    league_id integer references leagues (league_id),
    mp int NOT NULL,
    min int,
    "90s" FLOAT,
    starts int,
    subs int,
    unsub FLOAT,
    goals int,
    assists int,
    "G+A" int,
    non_penalty_goals FLOAT,
    penalties FLOAT,
    penalties_attempted FLOAT,
    penalties_missed FLOAT,
    position VARCHAR(255)
);
create index idx_season_stats_player_id
on season_stats(player_id);

\i docker-entrypoint-initdb.d/views.sql