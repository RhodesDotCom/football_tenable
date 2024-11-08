import uuid


class Config:
    DEBUG=True
    SECRET_KEY = "secret_key"
    DATA_API_URL = "http://data-api:5001"
    SESSION_API_URL = "http://session-api:5002"
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
