from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pygmy.config import config

app = Flask(__name__)
jwt = JWTManager(app)
CORS(app)
app.config['DEBUG'] = True
app.secret_key = config.secret

# This import is required. Removing this will break all hell loose.
import pygmy.rest.urls as _


def run():
    app.run(host=config.host, port=int(config.port))
