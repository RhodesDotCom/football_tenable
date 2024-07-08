import os
import psycopg2
import time
import pandas as pd
from sqlalchemy import create_engine, inspect


# DB_USER = os.environ.get('POSTGRES_USER')
# DB_PSWD = os.environ.get('POSTGRES_PASSWORD')
# DB_NAME = os.environ.get('POSTGRES_DB')
# DB_HOST = os.environ.get('POSTGRES_HOST')
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://stats_user:stats_password@postgres:5432/stats_db'


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


def check_table(engine, table_name):
    while True:
        print(f"Checking {table_name} exists in schema...")
        inspector = inspect(engine)
        if table_name in inspector.get_table_names(schema='stats_schema'):
            print(f'{table_name} found, continuing...')
            columns = inspector.get_columns(table_name=table_name, schema='stats_schema')
            print(f"Columns in {table_name}: {[col['name'] for col in columns]}")
            break
        else:
            print(f'Could not find {table_name}, retrying...')
            time.sleep(1)
            

wait_for_db()
try:
    print('Creating engine')
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    print('Engine created successfully')
except Exception as e:
    print(f"Error creating engine: ({e})")

# LOAD countries TABLE
countries_header = ['country_code', 'country']
countries = pd.read_csv('data/countries.csv', names=countries_header)
check_table(engine, 'countries')
try:
    countries.to_sql('countries', engine, schema='stats_schema', if_exists='replace', index=False)
except Exception as e:
    print(f'Error inserting into countries table: {e}')

# LOAD PLAYERS TABLE
players_header = ['player_id', 'player_name','nationality']
players = pd.read_csv('data/players.csv', names=players_header)
check_table(engine, 'players')
try:
    players.to_sql('players', engine, schema='stats_schema', if_exists='replace', index=False, method='multi')
except Exception as e:
    print(f'Error inserting into players table: {e}')


# LOAD PLAYERS_STATS TABLE
player_stats_headers = ['player_id','season','age','team','competition','MP','Min','90s','starts','subs','unsub','gls','ast','G+A','G-PK','PK','PKatt','PKm','pos']
player_stats = pd.read_csv('data/player_stats.csv', names=player_stats_headers)
check_table(engine, 'player_stats')
try:
    player_stats.to_sql('player_stats', engine, schema='stats_schema', if_exists='replace', index=False)
except Exception as e:
    print(f'Error inserting into player_stats table: {e}')


