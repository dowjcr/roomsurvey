from flask.cli import with_appcontext
import click
import csv

from roomsurvey.db import get_db

@click.command("import-allocations")
@with_appcontext
def import_allocations_command():
    db = get_db()

    with open("allocations.csv", newline="") as allocations_file:
        reader = csv.reader(allocations_file)
        # Skip the file header
        next(reader)

        # Some rooms don't have IDs, so we need to generate them within a safe range
        next_id = 1001

        for row in reader:
            id = -1
            if (int(row[4]) == -1):
                id = next_id
                next_id += 1
            else:
                id = int(row[4])

            print(id, row[3], row[0])
            db.execute("INSERT INTO room (id, shortname, inhabitant) VALUES (?, ?, ?)",
                    (id, row[3], row[0]))
            db.commit()

def init_app(app):
    app.cli.add_command(import_allocations_command)

def get_allocation_for_user(crsid):
    db = get_db()
    room_data = db.execute("SELECT * FROM room WHERE inhabitant=?", (crsid,)).fetchone()
    if room_data is None:
        return None
    return room_data["shortname"]
