import sqlalchemy
import sys
import os
import json
import time
from dotenv import load_dotenv


load_dotenv()


DB_USER = os.getenv('POSTGRES_USER')
DB_PSWD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')

SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PSWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SCHEMA = "stats_schema"


def main():
    try:
        print('Creating engine')
        engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI)
        print('Engine created successfully')
    except Exception as e:
        print(f"Error creating engine: ({e})")


    with open("tables.json", 'r') as f:
        tables = json.loads(f.read())
        
    for table in tables.keys():
        truncate_table(engine, table)


def truncate_table(engine: sqlalchemy.engine.Engine, table_name: str):
    try:
        conn = engine.connect()
        conn.execute(sqlalchemy.text(f'TRUNCATE TABLE {SCHEMA}.{table_name} CASCADE;'))
        conn.close()
    except Exception as e:
        print('Error truncating table...')
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
