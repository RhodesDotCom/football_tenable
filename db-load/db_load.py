import os
import psycopg2
import time
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
import json


load_dotenv()

DB_USER = os.getenv('POSTGRES_USER')
DB_PSWD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')

SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PSWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SCHEMA = "stats_schema"


def wait_for_db():
    while True:
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URI)
            conn = engine.connect()
            conn.close()
            print("Database is ready!")
            break
        except Exception as e:
            print(f"Database is not ready, waiting...  ({e})")
            time.sleep(1)


def check_table_exists(engine, table_name, check_columns=False):
    for i in range(10):
        print(f"Checking {table_name} exists in schema...")
        inspector = inspect(engine)
        if table_name in inspector.get_table_names(schema=SCHEMA):
            print(f'{table_name} found, continuing...')
            if check_columns:
                columns = inspector.get_columns(table_name=table_name, schema=SCHEMA)
                print(f"Columns in {table_name}: {[col['name'] for col in columns]}")
            return True
        else:
            print(f'Could not find {table_name}, retrying...')
            time.sleep(1)
    else:
        print(f"{table_name} could not be established")
        return False


def check_table_is_empty(engine, table_name):
    with engine.connect() as conn:
        result = conn.execute(text(f'SELECT COUNT(*) FROM {SCHEMA}.{table_name}'))
        count = result.scalar()
        return not bool(count)
    

def build_tables():
    try:
        print('Creating engine')
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        print('Engine created successfully')
    except Exception as e:
        print(f"Error creating engine: ({e})")

    with open('tables.json', 'r') as f:
        tables = json.loads(f.read())

    for table in tables.keys():
        if check_table_exists(engine, table) and check_table_is_empty(engine, table):
            print(f'loading data to {table}...')
            df = pd.read_csv(f'data/{table}.csv', names=tables[table])
            try:
                df.to_sql(table, engine, schema=SCHEMA, if_exists='append', index=False)
            except Exception as e:
                print(f'Error inserting into {table} table: {e}')
        else:
            print(f'skipping {table}...')
    print('all table data loaded')


wait_for_db()
build_tables()
