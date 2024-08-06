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
create index idx_player_stats_player_id
on player_stats(player_id);

CREATE TABLE IF NOT EXISTS countries (
    country_code VARCHAR(3) NOT NULL,
    country VARCHAR(255) NOT NULL,
    primary key(country_code, country)
);

CREATE OR REPLACE VIEW player_goals_by_season_ranked as
    select 
        p.player_name
        , ps.season
        , ps.team
        , ps.goals 
        , row_number() over (partition by season order by goals desc) as rn
    from player_stats ps
    join players p 
    on p.player_id = ps.player_id
    where goals is not null;

CREATE OR REPLACE VIEW goals_by_country_ranked as 
    select country, sum(goals) as total_goals
    from player_stats ps
    join players p 
    on p.player_id = ps.player_id 
    join countries c 
    on p.nationality = c.country_code
    group by country
    having sum(goals) > 0
    order by total_goals desc;

create view goals_and_assists as
    select player_name, season, team, goals, assists 
    from stats_schema.player_stats ps
    join stats_schema.players p
    on p.player_id = ps.player_id 
    order by player_name, season;

CREATE OR REPLACE VIEW team_top_scorers_by_season as
	select player_name, season, team, goals
	from (
	    select 
	        player_name
	        , season
	        , team
	        , goals
	        , dense_rank () over (partition by season, team order by goals desc) as rn
	    from player_stats ps
	    join players p
	    on p.player_id = ps.player_id
	    where goals is not null
	) as foo 
	where rn = 1;