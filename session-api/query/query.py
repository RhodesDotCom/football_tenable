from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import json
from flask import current_app

from config import Config


class Session:
    def get_conn(self):
        engine = create_engine(Config.SESSION_DB_URI)
        connection = engine.connect()
        try:
            yield connection
        finally:
            connection.close()


    def add_session_variable(self, id, data):
        
        sql = '''
            INSERT INTO session_schema.sessions
            (session_id, session_data, created_at, expires_at)
            VALUES (
                :session_id,
                :session_data,
                NOW(),
                NOW() + INTERVAL '2 hours'
            )'''
        
        for conn in self.get_conn():
            try:
                with conn.begin():
                    conn.execute(
                        text(sql), 
                        {'session_id': id, 'session_data': json.dumps(data)}
                    )
            except SQLAlchemyError as e:
                current_app.logger.error(e)
                # return {'success': False, 'message': str(e)}
    
    def read_session_variable(self, id):
        sql = '''
            SELECT session_data
            FROM session_schema.session
            WHERE session_id = :id;'''
        
        for conn in self.get_conn():
            results = conn.execute(text(sql), {'id':id})
        return results

