import uuid


class Config:
    DEBUG=True
    SESSION_DB_URI = 'postgresql+psycopg2://session_user:session_password@session-db:5432/session_db'

    SECRET_KEY = uuid.uuid4().hex