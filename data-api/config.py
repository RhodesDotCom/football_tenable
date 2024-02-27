import uuid


class Config:
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://stats_user:stats_password@postgres:5432/stats_db'
    SECRET_KEY = uuid.uuid4().hex