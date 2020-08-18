import flask
from flask import Flask, render_template, session, redirect, g, request
import os
from ucam_webauth.raven.flask_glue import AuthDecorator
import json

from roomsurvey.log import log

def create_app(test_config = None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
    )
    app.config.from_pyfile("config.py")

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    # Make sure that the instance directory exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)

    from . import db
    db.init_app(app)

    from . import user
    user.init_app(app)

    # Raven authentication

    # Request class boilerplate adapted from python-ucam-webauth
    # documentation, required so that we can make a hostname
    # whitelist

    class R(flask.Request):
        trusted_hosts = app.config["TRUSTED_HOSTS"]

    app.request_class = R
    auth_decorator = AuthDecorator(desc="Downing JCR Room Ballot Survey")

    # Create the routes

    from roomsurvey.syndicate import get_syndicate_for_user, get_syndicate_invitations, update_invitation, create_syndicate
    from roomsurvey.user import get_user, is_syndicatable

    @app.before_request
    def before_request_handler():
        g.crsid = auth_decorator.principal

        if g.crsid and request.path != "/logout" and not request.path.startswith("/static"):
            if not get_user(g.crsid):
                return render_template("unauthorised.html")

    @app.route("/dashboard")
    @auth_decorator
    def dashboard():
        return render_template("dashboard.html", syndicate=get_syndicate_for_user(g.crsid), invites=get_syndicate_invitations(g.crsid))

    @app.route("/syndicate")
    @auth_decorator
    def syndicate():
        return render_template("syndicate.html", syndicate=get_syndicate_for_user(g.crsid))

    @app.route("/syndicate/create", methods=["POST"])
    @auth_decorator
    def syndicate_create():
        invitees = json.loads(request.form['invitees-json'])

        for i in invitees:
            resp = is_syndicatable(i)
            if not resp["ok"]:
                raise Exception(resp["reason"])

        if len(invitees) > 8 or len(invitees) < 0:
            raise Exception("Bad syndicate length")
        
        if len(set(invitees)) != len(invitees):
            raise Exception("Duplicates")

        if g.crsid not in invitees:
            raise Exception("Must invite self")

        log(g.crsid, "created syndicate and invited " + ",".join(invitees))
        create_syndicate(g.crsid, invitees)
        return redirect("/dashboard", 302)

    @app.route("/invite")
    @auth_decorator
    def invite():
        return render_template("invite.html", invites=get_syndicate_invitations(g.crsid))

    @app.route("/invite/accept", methods=["POST"])
    @auth_decorator
    def invite_accept():
        log(g.crsid, "has accepted a syndicate invitation")
        update_invitation(g.crsid, True)
        return redirect("/dashboard", 302)

    @app.route("/invite/reject", methods=["POST"])
    @auth_decorator
    def invite_reject():
        log(g.crsid, "has rejected a syndicate invitation")
        update_invitation(g.crsid, False)
        return redirect("/dashboard", 302)

    @app.route("/api/is_syndicatable/<crsid>")
    @auth_decorator
    def api_is_syndicatable(crsid):
        resp = is_syndicatable(crsid)
        return json.dumps(resp)

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
