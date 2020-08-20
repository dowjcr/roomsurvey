from flask.cli import with_appcontext
import click
import smtplib

from roomsurvey.db import get_db

# TODO: remove hard-coded downingjcr values from this whole file

def queue_email(to, subject, body):
    db = get_db()

    db.execute("INSERT INTO mail_queue (recipient, subject, body) VALUES (?, ?, ?)", (to, subject, body))
    db.commit()

def syndicate_mail(inviter, invitee):
    to = invitee+"@cam.ac.uk"
    subject = "Downing JCR Room Ballot"
    body = "Hello,\n\nThe user "+inviter+" has invited you to join their syndicate. To view the invitation, please click on the following link:\n\nhttps://ballot.downingjcr.co.uk/invite\n\nIf you have any questions, feel free to reply to this email."

    queue_email(to, subject, body)

@click.command("send-emails")
@with_appcontext
def send_emails_command():
    # Right now only sending over plaintext to the local mail server is supported
    SMTP_HOST = "localhost"
    SMTP_PORT = 25
    SMTP_SENDER = "noreply@ballot.downingjcr.co.uk"
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
