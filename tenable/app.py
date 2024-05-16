from flask import Flask, redirect, url_for

from tenable_ui.routes import game_bp
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(game_bp, url_prefix='/game')


@app.route('/')
def home():
    return redirect(url_for('game_bp.main_menu'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')