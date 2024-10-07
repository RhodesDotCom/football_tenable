import os
import psycopg2
import time
import pandas as pd
from sqlalchemy import create_engine, inspect, text


# DB_USER = os.environ.get('POSTGRES_USER')
# DB_PSWD = os.environ.get('POSTGRES_PASSWORD')
# DB_NAME = os.environ.get('POSTGRES_DB')
# DB_HOST = os.environ.get('POSTGRES_HOST')
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://stats_user:stats_password@stats-db:5432/stats_db'
SCHEMA = "stats_schema"


TABLE_HEADERS = {
    "countries": ['country_code', 'country'],
    "players": ['player_id', 'player_name','nationality'],
    "player_stats": ['player_id','season','age','team','competition','mp','min','90s','starts','subs','unsub','goals','assists','G+A','non_penalty_goals','penalties','penalties_attempted','penalties_missed','position'],
}


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

    tables = ['countries', 'players', 'player_stats']

    for table in tables:
        if check_table_exists(engine, table) and check_table_is_empty(engine, table):
            print(f'loading data to {table}...')
            df = pd.read_csv(f'data/{table}.csv', names=TABLE_HEADERS[table])
            try:
                df.to_sql(table, engine, schema=SCHEMA, if_exists='append', index=False)
            except Exception as e:
                print(f'Error inserting into {table} table: {e}')
        else:
            print(f'skipping {table}...')
    print('all table data loaded')


wait_for_db()
build_tables()
