from sqlalchemy import create_engine, text
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


    def get_all_players(self):
        for conn in self.get_conn():
            
            sql= '''select distinct player
            FROM stats_schema.player_stats
            order by player;'''
            
            results = conn.execute(text(sql))
            
            return {'players': [row[0] for row in results]}

    def get_golden_boot_winners(self):

        for conn in self.get_conn():

            sql = '''SELECT player, season, goals
            FROM stats_schema.player_goals_by_season_ranked
            WHERE rn = 1;'''

            results = conn.execute(text(sql))
            columns = results.keys()
        
            return self.format_results(columns, results)
        
    def get_goals_and_assists(self, goals:int, assists:int):
            
        for conn in self.get_conn():

            sql = text('''SELECT player, season, goals, ast
            FROM stats_schema.goals_and_assists
            WHERE goals >= :goals and ast >= :assists;''')

            results = conn.execute(sql, {'goals': goals, 'assists': assists})
            columns = results.keys()
            current_app.logger.info(results)
            return self.format_results(columns, results)
        
    def get_goals_by_nation(self):
            
        for conn in self.get_conn():

            sql = 'SELECT nationality, total_goals FROM stats_schema.goals_by_country_ranked;'

            results = conn.execute(text(sql))
            columns = results.keys()
        
            return self.format_results(columns, results)
    
    
         