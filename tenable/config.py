import uuid


class Config:
    DEBUG=True
    SECRET_KEY = uuid.uuid4().hex
    DATA_API_URL = "http://data-api:5001"
