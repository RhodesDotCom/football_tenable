from sqlalchemy import create_engine, text, insert, Table, MetaData
from sqlalchemy.exc import SQLAlchemyError
import json
from flask import current_app, jsonify
from datetime import datetime as dt
from datetime import timedelta

from config import Config


class Session:
    def __init__(self) -> None:
        self.engine = create_engine(Config.SESSION_DB_URI)
        self.metadata = MetaData()
        self.sessions_table = Table(
            'sessions',
            self.metadata,
            autoload_with=self.engine,
            schema='session_schema'
        )
    

    def get_conn(self):
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()


    def add_session_variable(self, data):
        
        sql = (
            insert(self.sessions_table).
            values(
                session_data=data,
                created_at=dt.now(),
                expires_at=dt.now() + timedelta(hours=2)
            )
        )

        for conn in self.get_conn():
            try:
                with conn.begin():

                    r = conn.execute(sql)
                return r.inserted_primary_key, 201
            except SQLAlchemyError as e:
                current_app.logger.error(e)
                return jsonify({'error': str(e)}), 500 


    def read_session_variable(self, id):
        sql = '''
            SELECT session_data
            FROM session_schema.sessions
            WHERE session_id = :id;'''
        
        for conn in self.get_conn():
            r = conn.execute(text(sql), {'id':id})

            data = r.scalar()
            
            if data:
                return data
