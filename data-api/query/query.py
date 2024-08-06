import sqlalchemy
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from flask import current_app

from config import Config


class Queries:
    def get_conn(self):
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        connection = engine.connect()
        try:
            yield connection
        finally:
            connection.close()


    def format_results(self, columns, rows):
            return [(dict(zip(columns, row))) for row in rows]


    def get_inputs(self, category='player_name'):
        for conn in self.get_conn():

            inspector = inspect(conn)
            columns = []
            try:
                columns += inspector.get_columns('player_stats', schema='stats_schema')
                columns += inspector.get_columns('countries', schema='stats_schema')
                columns += inspector.get_columns('players', schema='stats_schema')
            except sqlalchemy.exc.NoSuchTableError as e:
                print(f"Error: {e}")
                raise           

            columns = [c['name'] for c in columns]

            if category not in columns:
                current_app.logger.error('column not in table')
                return None
            else:

                sql = text(f"""select distinct {category}
                        from stats_schema.player_stats ps
                        join stats_schema.players p
                        on p.player_id = ps.player_id
                        join stats_schema.countries c
                        on p.nationality = c.country_code
                        order by {category};""")

                results = conn.execute(sql)

                return {category: [row[0] for row in results]}


    def get_golden_boot_winners(self):
        for conn in self.get_conn():

            sql = '''SELECT player_name, season, goals
            FROM stats_schema.player_goals_by_season_ranked
            WHERE rn = 1;'''

            results = conn.execute(text(sql))
            columns = results.keys()
        
            return self.format_results(columns, results)
        

    def get_goals_and_assists(self, goals:int, assists:int):   
        for conn in self.get_conn():

            sql = text('''SELECT player_name, season, goals, assists
            FROM stats_schema.goals_and_assists
            WHERE goals >= :goals and assists >= :assists;''')

            results = conn.execute(sql, {'goals': goals, 'assists': assists})
            columns = results.keys()
            current_app.logger.info(results)
            return self.format_results(columns, results)

      
    def get_goals_by_nation(self):
            
        for conn in self.get_conn():

            sql = 'SELECT country, total_goals FROM stats_schema.goals_by_country_ranked;'

            results = conn.execute(text(sql))
            columns = results.keys()
        
            return self.format_results(columns, results)
    

    def get_team_topscorers_by_season(self):
        for conn in self.get_conn():
            sql = '''
                select player_name, season, team, goals
                from (
                    select 
                        player_name
                        , season
                        , team
                        , goals
                        , row_number () over (partition by season, team order by goals desc) as rn
                    from player_stats ps
                    join players p
                    on p.player_id = ps.player_id
                    where goals is not null
                ) as foo 
                where rn = 1
            '''
            results = conn.execute(text(sql))
            columns = results.keys()

            return self.format_results(columns, results)


    def get_team_total_goals(self):
        for conn in self.get_conn():
            sql = '''select team, sum(goals) as total_goals from player_stats ps group by team order by sum(goals) desc;'''

            results = conn.execute(text(sql))
            columns = results.keys()

            return self.format_results(columns, results)


    
         