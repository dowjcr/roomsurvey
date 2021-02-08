import flask
from flask import Flask, render_template, session, redirect, g, request, abort
import os
from ucam_webauth.raven.flask_glue import AuthDecorator
import json
import time

from roomsurvey.log import log

def create_app(test_config = None):

    # Create the app object and import some config

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

    # Load middleware and commands

    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)

    from . import db
    db.init_app(app)

    from . import user
    user.init_app(app)

    from . import mail
    mail.init_app(app)

    from . import allocations
    allocations.init_app(app)

    from . import review
    review.init_app(app)

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
    from roomsurvey.user import get_user, get_year, is_syndicatable
    from roomsurvey.survey import get_survey_data, import_survey_data, log_survey_data
    from roomsurvey.allocations import get_allocation_for_user
    from roomsurvey.review import has_reviewed, check_review, write_review

    @app.before_request
    def before_request_handler():
        g.crsid = auth_decorator.principal

        # fullname is ONLY set if the user is both authenticated AND in the database
        g.fullname = None

        if g.crsid:
            g.fullname = get_user(g.crsid)
            g.user_year = get_year(g.crsid)

        if (
                g.crsid and
                request.path != "/logout" and
                not request.path.startswith("/static") and
                not g.fullname
           ):
            return render_template("unauthorised.html")

        g.current_time = int(time.time())

    @app.route("/dashboard")
    @auth_decorator
    def dashboard():
        return render_template("dashboard.html", syndicate=get_syndicate_for_user(g.crsid), invites=get_syndicate_invitations(g.crsid), survey_data=get_survey_data(g.crsid))

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
                return abort(400)

        if len(invitees) > 8 or len(invitees) < 0:
            return abort(400)
        
        if len(set(invitees)) != len(invitees):
            return abort(400)

        if g.crsid not in invitees:
            return abort(400)

        if g.current_time > app.config["CLOSE_SYNDICATES"]:
            return abort(400)

        log(g.crsid, "created syndicate and invited " + ",".join(invitees))
        if request.form["want-to-stay"] == "yes":
            log(g.crsid, "said their syndicate wants to stay")

        create_syndicate(g.crsid, invitees, request.form["want-to-stay"])
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
        log(g.crsid, "has rejected a syndicate invitation (WARN)")
        update_invitation(g.crsid, False)
        return redirect("/dashboard", 302)

    @app.route("/api/is_syndicatable/<crsid>")
    @auth_decorator
    def api_is_syndicatable(crsid):
        resp = is_syndicatable(crsid)
        return json.dumps(resp)

    @app.route("/api/survey_data/"+app.config["COGNITOFORMS_KEY"], methods=["POST"])
    @csrf.exempt
    def api_survey_data():
        if request.content_length > 65536:
            return abort(413)

        log_survey_data(request.get_data())
        return import_survey_data(request.get_json())

    @app.route("/survey")
    @auth_decorator
    def survey():
        if g.current_time < app.config["SHOW_SURVEY"]:
            return abort(403)

        return render_template("survey.html", survey_data=get_survey_data(g.crsid))

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

    @app.route("/allocations")
    @auth_decorator
    def allocations():
        if g.current_time < app.config["SHOW_ALLOCATIONS"]:
            return abort(403)

        return render_template("allocations.html")

    @app.route("/review")
    @auth_decorator
    def review():
        if not app.config["ROOM_REVIEWS"]:
            return render_template("review_no.html")

        room = get_allocation_for_user(g.crsid)
        if room is None:
            return abort(403)

        if has_reviewed(g.crsid):
            return render_template("review_thanks.html")

        return render_template("review.html", room=room)

    @app.route("/review", methods=["POST"])
    @auth_decorator
    def leave_review():
        if not app.config["ROOM_REVIEWS"]:
            return abort(403)

        room = get_allocation_for_user(g.crsid)
        if room is None:
            return abort(403)

        if has_reviewed(g.crsid):
            return abort(403)

        if not check_review(request.form):
            return abort(400)

        write_review(g.crsid, room, request.form)
        return render_template("review_thanks.html")

    # cheeky jinja function override so that we can make database calls from the templates
    # this is a bit of a hack but it makes the python code a lot cleaner
    app.jinja_env.globals.update(get_user=get_user)

    # The app is complete and ready to accept requests

    return app
