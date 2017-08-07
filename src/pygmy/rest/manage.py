from flask import Flask
from flask_cors import CORS
from pygmy.config import config

app = Flask(__name__)
CORS(app)
app.config['DEBUG'] = True
# This import is required.
import pygmy.rest.urls as _


def run():
    app.run(host=config.host, port=int(config.port))
