import string
import random
import click
import csv
from flask.cli import with_appcontext

from roomsurvey.db import get_db

def get_user(crsid):
    # returns full name if user exists, else false
    
    db = get_db()

    user_data = db.execute("SELECT forename,surname FROM user WHERE crsid=?", (crsid,)).fetchone()

    if user_data:
        return user_data["forename"]+" "+user_data["surname"]

    return False

def is_syndicatable(crsid):
    # Checks if a user is in a fit state to join a syndicate

    db = get_db()

    user_data = db.execute("SELECT syndicate FROM user WHERE crsid=?", (crsid,)).fetchone()

    if not user_data:
        return {"ok": False, "reason": "This person is not in the ballot."}
    if user_data["syndicate"]:
        return {"ok": False, "reason": "This user is already part of another syndicate."}

    invite_data = db.execute(
        "SELECT id FROM syndicate_invitation WHERE recipient=? AND used=0",
        (crsid,)
    ).fetchone()

    if invite_data:
        return {"ok": False, "reason": (
            "This user has already been invited to another syndicate. Please allow them to deal with life's "
            "dillemas one at a time."
        )}

    full_name = get_user(crsid)

    return {"ok": True, "name": full_name}

@click.command("import-users")
@with_appcontext
def import_users_command():
    db = get_db()

    with open("users.csv", newline="") as users_file:
        # csv format: crsid,forename,surname,year
        # cf. https://github.com/dowjcr/ucam-lookup-byyear

        count = 0

        reader = csv.reader(users_file)
        for row in reader:
            db.execute("INSERT INTO user (crsid, forename, surname, year, formtoken) VALUES (?, ?, ?, ?, ?)", (
                row[0],
                row[1],
                row[2],
                row[3],
                ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))
            ))
            db.commit()
            count += 1

    print("Imported", str(count), "users")

def init_app(app):
    app.cli.add_command(import_users_command)
