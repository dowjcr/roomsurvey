import json
import time
import click
from flask import abort
from flask.cli import with_appcontext

from roomsurvey.db import get_db
from roomsurvey.log import log
from roomsurvey.syndicate import get_syndicate_for_user
from roomsurvey.mail import survey_reminder_mail

def get_survey_data(crsid):
    db = get_db()

    survey_data = db.execute('SELECT has_filled, formtoken FROM user WHERE crsid=?', (crsid,)).fetchone()

    return survey_data

def log_survey_data(raw_data):
    db = get_db()

    db.execute("INSERT INTO form_payload (time, json) VALUES (?, ?)", (int(time.time()), raw_data))
    db.commit()

def import_survey_data(data):
    if not data:
        return abort(400)
    if "CRSid" not in data:
        return abort(400)
    if "FormToken" not in data:
        return abort(400)

    db = get_db()

    user_data = db.execute("SELECT formtoken, has_filled FROM user WHERE crsid=?", (data["CRSid"],)).fetchone()

    if not user_data:
        log(data["CRSid"], "submitted the form despite not existing (WARN)")
        return abort(400)

    if user_data["formtoken"] != data["FormToken"]:
        log(data["CRSid"], "received a response with an incorrect FormToken (WARN)")
        return abort(400)

    if user_data["has_filled"] == 1:
        log(data["CRSid"], "filled in the form more than once (WARN)")

    log(data["CRSid"], "filled in the form ok")

    db.execute("UPDATE user SET has_filled=1 WHERE crsid=?", (data["CRSid"],))
    db.commit()

    return "OK\n"

@click.command("send-survey-reminder")
@with_appcontext
def send_survey_reminder_command():
    if not click.confirm("You are about to send an email to A LOT OF PEOPLE. Are you sure?"):
        return

    db = get_db()

    count = 0

    # get all syndicates where somebody has not filled in the form

    syndicate_list = db.execute("SELECT crsid FROM user WHERE syndicate NOT NULL AND has_filled = 0"
            " GROUP BY syndicate")
    for syndicate in syndicate_list:
        syndicate_data = get_syndicate_for_user(syndicate["crsid"])
        email_recipients = (
                list(map(lambda x: x["crsid"], syndicate_data["others"])) +
                [syndicate_data["owner"]]
        )
        survey_reminder_mail(email_recipients)
        count += len(email_recipients)

    print("Queued %d emails" % count)
    print("They will send on the next run of send-emails")

def init_app(app):
    app.cli.add_command(send_survey_reminder_command)
