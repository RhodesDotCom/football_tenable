from flask import Flask, redirect, url_for
import logging


from tenable_ui.routes import game_bp
from config import Config
from cache import cache


app = Flask(__name__)
app.config.from_object(Config)

cache.init_app(app)

app.register_blueprint(game_bp, url_prefix='/game')

#I think this module is broken, logging level ERROR or higher == NOTSET
logging.getLogger('country_converter').setLevel(logging.ERROR)





@app.route('/')
def home():
    return redirect(url_for('game_bp.main_menu'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')