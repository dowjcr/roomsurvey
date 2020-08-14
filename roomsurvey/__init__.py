import flask
from flask import Flask, render_template
import os
from ucam_webauth.raven.flask_glue import AuthDecorator

# Request class boilerplate adapted from python-ucam-webauth
# documentation, required so that we can make a hostname
# whitelist

class R(flask.Request):
    trusted_hosts = {"localhost"} # TODO

def create_app(test_config = None):
    # Boilerplate factory function adapted from Flask docs

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = os.urandom(16), # TODO: maybe store a persistent key
        DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    # Make sure that the instance directory exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    # Raven authentication
    app.request_class = R
    auth_decorator = AuthDecorator(desc="Downing JCR Room Ballot Survey")

    # Create the routes
    @app.route("/dashboard")
    @auth_decorator
    def secret():
        return "congratulations, you're logged in as "+auth_decorator.principal

    @app.route("/")
    def landing():
        return render_template("landing.html")

    return app
