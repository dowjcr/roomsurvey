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

@click.command("import-users")
@with_appcontext
def import_users_command():
    db = get_db()
    f = open("crsids.txt", "r")

    count = 0

    for crsid in f:
        db.execute("INSERT INTO user (crsid) VALUES (?)", (crsid.strip(),))
        db.commit()
        count += 1

    print("Imported", str(count), "users")

def init_app(app):
    app.cli.add_command(import_users_command)
