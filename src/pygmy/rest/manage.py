from flask import Flask, Blueprint
from pygmy.config import config

app = Flask(__name__)
app.config['DEBUG'] = True
import pygmy.rest.urls as _


def run():
    app.run(host=config.host, port=int(config.port))
