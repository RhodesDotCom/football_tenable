CREATE SCHEMA IF NOT EXISTS stats_schema;
SET search_path TO stats_schema;

create table if not exists players (
	player_id SERIAL primary key,
	player_name varchar(255) not null,
	nationality varchar(255)
);

CREATE TABLE IF NOT EXISTS player_stats (
	stats_id SERIAL primary key,
	player_id integer references players (player_id),
    season varchar(255),
	"age" int,
    team VARCHAR(255),
    competition VARCHAR(255),
    MP int NOT NULL,
    min int,
    "90s" FLOAT,
    starts int,
    subs int,
    unsub FLOAT,
    goals int,
    ast int,
    "G+A" int,
    non_penalty_goals FLOAT,
    penalties FLOAT,
    PK_attempted FLOAT,
    PK_missed FLOAT,
    pos VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS countries (
    country_code VARCHAR(3) NOT NULL,
    country VARCHAR(255) NOT NULL,
    primary key(country_code, country)
);