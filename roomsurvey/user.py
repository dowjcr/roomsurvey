import string
import random
import click
from flask.cli import with_appcontext

from roomsurvey.db import get_db

def get_user(crsid):
    # returns true if user exists, else false
    
    db = get_db()

    user_data = db.execute("SELECT crsid FROM user WHERE crsid=?", (crsid,)).fetchone()

    if user_data:
        return True

    return False

def is_syndicatable(crsid):
    # Checks if a user is in a fit state to join a syndicate

    db = get_db()

    user_data = db.execute("SELECT syndicate FROM user WHERE crsid=?", (crsid,)).fetchone()

    if not user_data:
        return {"ok": False, "reason": "This person is not in the ballot."}
    if user_data["syndicate"]:
        return {"ok": False, "reason": "This user is already part of another syndicate."}

    invite_data = db.execute("SELECT id FROM syndicate_invitation WHERE recipient=? AND used=0", (crsid,)).fetchone()

    if invite_data:
        return {"ok": False, "reason": "This user has already been invited to another syndicate. Please allow them to deal with life's dillemas one at a time."}

    return {"ok": True}

@click.command("import-users")
@with_appcontext
def import_users_command():
    db = get_db()
    f = open("crsids.txt", "r")

    count = 0

    for crsid in f:
        db.execute("INSERT INTO user (crsid, formtoken) VALUES (?, ?)", (
            crsid.strip(),
            ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        ))
        db.commit()
        count += 1

    print("Imported", str(count), "users")

def init_app(app):
    app.cli.add_command(import_users_command)
