import uuid


class Config:
    DEBUG=True
    STATS_DB_URI = 'postgresql+psycopg2://stats_user:stats_password@stats-db:5432/stats_db'
    SECRET_KEY = uuid.uuid4().hex