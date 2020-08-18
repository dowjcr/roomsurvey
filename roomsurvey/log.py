from roomsurvey.db import get_db

def log(crsid, message):
    db = get_db()

    db.execute("INSERT INTO log_message (user, message) VALUES (?, ?)", (crsid, message))
    db.commit()
