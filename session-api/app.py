from flask import Flask
import logging

from query.routes import session_bp
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(session_bp)


formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s [%(filename)s:%(lineno)d]: %(message)s'
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
app.logger.handlers.clear()
app.logger.addHandler(handler)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)