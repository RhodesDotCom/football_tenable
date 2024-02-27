from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from flask import current_app

from config import Config


class Queries:
    # def get_conn(self):
    #     current_app.logger.info(Config.SQLALCHEMY_DATABASE_URI)
    #     engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    #     connection = engine.connect()
    #     try:
    #         yield connection
    #     finally:
    #         connection.close()
    def format_results(self, columns, rows):
            return [(dict(zip(columns, row))) for row in rows]

    def get_golden_boot_winners(self):
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
        conn = engine.connect()

        sql = '''SELECT player, season, goals
        FROM stats_schema.player_goals_by_season_ranked
        WHERE rn = 1;'''

        results = conn.execute(text(sql))
        columns = results.keys()

        conn.close()
        
        return self.format_results(columns, results)