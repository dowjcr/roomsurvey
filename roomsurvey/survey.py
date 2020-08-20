import json
import time
from flask import abort

from roomsurvey.db import get_db
from roomsurvey.log import log

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

    db.execute("UPDATE user SET has_filled=1 WHERE crsid=?", (data["CRSid"],))
    db.commit()

    return "OK\n"
