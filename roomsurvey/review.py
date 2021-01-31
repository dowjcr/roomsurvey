from flask.cli import with_appcontext
import click

from roomsurvey.db import get_db
from roomsurvey.mail import review_mail

def has_reviewed(crsid):
    db = get_db()

    review = db.execute("SELECT author FROM review WHERE author=?", (crsid,)).fetchone()

    if review is None:
        return False
    else:
        return True

def check_review(form_data):
    fields = ["title", "layout-rating", "facilities-rating", "noise-rating", "overall-rating", "text"]
    for f in fields:
        if form_data[f].strip() == "":
            return False

    for f in ["layout-rating", "facilities-rating", "noise-rating", "overall-rating"]:
        rating = 0
        try:
            rating = int(form_data[f][:1])
        except ValueError:
            return False
        if rating < 1 or rating > 5:
            return False

    return True

def write_review(author, room, form_data):
    db = get_db()
    db.execute("INSERT INTO review (author, room, layout_rating, facilities_rating, noise_rating, overall_rating, title, body) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (author, room, int(form_data["layout-rating"][:1]), int(form_data["facilities-rating"][:1]),
                int(form_data["noise-rating"][:1]), int(form_data["overall-rating"][:1]), form_data["title"],
                form_data["text"]))
    db.commit()

@click.command("send-review-reminder")
@with_appcontext
def send_review_reminder_command():
    if not click.confirm("You are about to send an email to EVERYBODY. Are you sure?"):
        return

    db = get_db()

    rooms = db.execute("SELECT * FROM room").fetchall()
    count = 0

    for room in rooms:
        if room["inhabitant"] is None:
            continue
        review_mail(room["inhabitant"], room["shortname"])
        count += 1

    print("Queued %d emails" % count)
    print("They will be sent next time send-emails runs.")

def init_app(app):
    app.cli.add_command(send_review_reminder_command)
