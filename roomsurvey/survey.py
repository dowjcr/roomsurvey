from roomsurvey.db import get_db

def get_survey_data(crsid):
    db = get_db()

    survey_data = db.execute('SELECT has_filled, formtoken FROM user WHERE crsid=?', (crsid,)).fetchone()

    return survey_data
