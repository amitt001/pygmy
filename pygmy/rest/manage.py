import datetime
import os
from flask import request, jsonify

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pygmy.config import config

app = Flask(__name__)
CORS(app)
app.config['DEBUG'] = config.debug
app.config['MAX_CONTENT_LENGTH'] = 256 * 1024

@app.before_request
def demo_accounts_disabled():
    if os.environ.get('PYGMY_DEMO_MODE') == '1':
        if (request.path.startswith('/api/user') or
                request.path.rstrip('/') in ('/api/login', '/token/refresh')):
            return jsonify(error='Signup and login are not available in the demo. Self-host Pygmy from GitHub to use accounts.'), 403
app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', datetime.timedelta(minutes=1))
app.config.setdefault('JWT_REFRESH_TOKEN_EXPIRES', datetime.timedelta(days=7))
app.config.setdefault('JWT_HEADER_NAME', 'JWT_Authorization')
app.secret_key = config.secret

jwt = JWTManager(app)

# This import is required. Removing this will break all hell loose.
import pygmy.rest.urls as _


def run():
    app.run(host=config.host, port=int(config.port))
