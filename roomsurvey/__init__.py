import flask
from flask import Flask, render_template, session, redirect, g
import os
from ucam_webauth.raven.flask_glue import AuthDecorator

# Request class boilerplate adapted from python-ucam-webauth
# documentation, required so that we can make a hostname
# whitelist

class R(flask.Request):
    trusted_hosts = {"localhost", "192.168.1.245"} # TODO

# TODO: some kind of logging

def create_app(test_config = None):
    # Boilerplate factory function adapted from Flask docs

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        #SECRET_KEY = os.urandom(16), # TODO: maybe store a persistent key
        SECRET_KEY = "development1337", # TODO REALLY IMPORTANT CHANGE THIS
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
    # TODO: only allow students who are balloting to log in
    app.request_class = R
    auth_decorator = AuthDecorator(desc="Downing JCR Room Ballot Survey")

    @app.before_request
    def before_request_handler():
        g.crsid = auth_decorator.principal

    # Create the routes

    from roomsurvey.syndicate import get_syndicate_for_user, get_syndicate_invitations, update_invitation

    @app.route("/dashboard")
    @auth_decorator
    def dashboard():
        return render_template("dashboard.html", syndicate=get_syndicate_for_user(g.crsid), invites=get_syndicate_invitations(g.crsid))

    @app.route("/syndicate")
    @auth_decorator
    def syndicate():
        return render_template("syndicate.html", syndicate=get_syndicate_for_user(g.crsid))

    @app.route("/invite")
    @auth_decorator
    def invite():
        return render_template("invite.html", invites=get_syndicate_invitations(g.crsid))

    @app.route("/invite/accept", methods=["POST"])
    @auth_decorator
    def invite_accept():
        update_invitation(g.crsid, True)
        return redirect("/dashboard", 302)

    @app.route("/invite/reject", methods=["POST"])
    @auth_decorator
    def invite_reject():
        update_invitation(g.crsid, False)
        return redirect("/dashboard", 302)

    @app.route("/")
    def landing():
        try:
            session["_ucam_webauth"]["state"]["principal"]
            return redirect("/dashboard", 302)
        except KeyError:
            return render_template("landing.html")

    @app.route("/about")
    @auth_decorator
    def about():
        return render_template("about.html")

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect("/", code=302)

    return app
