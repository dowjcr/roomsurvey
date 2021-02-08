from flask.cli import with_appcontext
import click
import smtplib

from roomsurvey.db import get_db
from roomsurvey.user import get_user

# TODO: remove hard-coded downingjcr values from this whole file

def queue_email(to, subject, body):
    db = get_db()

    db.execute("INSERT INTO mail_queue (recipient, subject, body) VALUES (?, ?, ?)", (to, subject, body))
    db.commit()

# Probably best to use the templating engine for these emails, but this works fine for now

def syndicate_mail(inviter, invitee):
    to = invitee+"@cam.ac.uk"
    subject = "Downing JCR Room Ballot"
    body = ("Hello,\n\n"
            "%s has invited you to join their syndicate. To view the invitation,\n"
            "please click on the following link:\n\n"
            "https://ballot.downingjcr.co.uk/invite\n\n"
            "If you have any questions, please feel free to reply to this email.") % get_user(inviter)

    queue_email(to, subject, body)

def review_mail(recipient, room):
    to = recipient+"@cam.ac.uk"
    subject = "Downing JCR Room Ballot: Please leave a review of your room!"
    body = ("Hi everyone,\n\n"
            "Hope you are all keeping well at the moment.\n\n"
            "You're receiving this email because our records indicate you have\n"
            "been living in room %s.\n\n"
            "It would be a huge help to us if you could leave a review of your\n"
            "room - this helps us determine room pricing and gives future\n"
            "students more information to help them choose their rooms.\n\n"
            "You can leave a review by clicking on the following link:\n"
            "https://ballot.downingjcr.co.uk/review\n\n"
            "If the room we have on record for you is not correct, or you have\n"
            "any issues leaving a review, please just reply to this email and\n"
            "we will do our best to sort it out.\n\n"
            "Thanks in advance for your help!\n\n"
            "Sending Downing love from afar,\n\n"
            "Lawrence, Tammy and the JCR") % room

    queue_email(to, subject, body)

@click.command("send-emails")
@with_appcontext
def send_emails_command():
    # Right now only sending over plaintext to the local mail server is supported
    SMTP_HOST = "localhost"
    SMTP_PORT = 25
    SMTP_SENDER = "system@ballot.downingjcr.co.uk"
    SMTP_REPLYTO = "internet@jcr.dow.cam.ac.uk"

    db = get_db()

    emails = db.execute("SELECT * FROM mail_queue").fetchall()

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        for email in emails:
            server.sendmail(
                SMTP_SENDER,
                email["recipient"],
                "Subject: "+email["subject"]+
                    "\nTo: "+email["recipient"]+
                    "\nFrom: "+SMTP_SENDER+
                    "\nReply-To: "+SMTP_REPLYTO+
                    "\n\n"+email["body"]
            )

            db.execute("DELETE FROM mail_queue WHERE id=?", (email["id"],))
            db.commit()

def init_app(app):
    app.cli.add_command(send_emails_command)
