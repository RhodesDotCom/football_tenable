import uuid


class Config:
    DEBUG=True
    SESSION_DB_URI = 'postgresql+psycopg2://sesssion_user:sesssion_password@postgres:5433/sesssion_db'
    SECRET_KEY = uuid.uuid4().hex