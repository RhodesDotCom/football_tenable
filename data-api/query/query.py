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


    def get_inputs(self, category='player'):
        for conn in self.get_conn():

            # column = sqlalchemy.column(category)
            # metadata = sqlalchemy.MetaData()
            # table = sqlalchemy.Table(
            #     'player_stats',
            #     metadata,
            #     autoload_with=conn,
            #     schema='stats_schema'
            # )
            # query = sqlalchemy.select(
            #     column.distinct()
            # ).select_from(
            #     table
            # ).order_by(column)
            
            # # sql= text('''select distinct :category
            # # FROM stats_schema.player_stats
            # # order by :category;''')

            inspector = inspect(conn)
            columns = []
            try:
                columns += inspector.get_columns('player_stats', schema='stats_schema')
                columns += inspector.get_columns('countries', schema='stats_schema')
            except sqlalchemy.exc.NoSuchTableError as e:
                print(f"Error: {e}")
                raise

            

            columns = [c['name'] for c in columns]

            if category not in columns:
                current_app.logger.error('column not in table')
                return None
            else:

                sql = text(f"""select distinct {category}
                        from stats_schema.player_stats
                        join stats_schema.countries 
                        on nationality = country_code
                        order by {category};""")

                results = conn.execute(sql)

                return {category: [row[0] for row in results]}

    def get_all_nations(self):
        for conn in self.get_conn():
            
            sql= '''select distinct nationality
            FROM stats_schema.player_stats
            order by nationality;'''
            
            results = conn.execute(text(sql))
            
            return {'nation': [row[0] for row in results]}

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
    
    
         