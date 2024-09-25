from flask import Flask

from query.routes import query_bp
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(query_bp)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)