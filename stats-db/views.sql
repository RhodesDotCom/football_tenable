CREATE OR REPLACE VIEW player_goals_by_season_ranked as
    select 
        p.player_name
        , ss.season
        , ss.team
        , ss.goals 
        , row_number() over (partition by season order by goals desc) as rn
    from stats_schema.season_stats ss
    join stats_schema.players p 
    on p.player_id = ss.player_id
    where goals is not null;

CREATE OR REPLACE VIEW goals_by_country_ranked as 
    select country, sum(goals) as total_goals
    from stats_schema.season_stats ss
    join stats_schema.players p 
    on p.player_id = ss.player_id 
    join stats_schema.countries c 
    on p.nationality = c.country_code
    group by country
    having sum(goals) > 0
    order by total_goals desc;

CREATE OR REPLACE VIEW goals_and_assists as
    select player_name, season, team, goals, assists 
    from stats_schema.season_stats ss
    join stats_schema.players p
    on p.player_id = ss.player_id 
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
	    from stats_schema.season_stats ss
	    join stats_schema.players p
	    on p.player_id = ss.player_id
	    where goals is not null
	) as foo 
	where rn = 1;