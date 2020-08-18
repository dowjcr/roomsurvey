from roomsurvey.db import get_db

def create_user_record(crsid):
    # Creates a row in the database for this user IF they don't currently have one

    db = get_db()

    row = db.execute('SELECT crsid FROM user WHERE crsid=?', (crsid,)).fetchone()

    if row is not None:
        return

    db.execute('INSERT INTO user (crsid) VALUES (?)', (crsid,))
    db.commit()
