from roomsurvey.db import get_db

def queue_email(to, subject, body):
    db = get_db()

    db.execute("INSERT INTO mail_queue (recipient, subject, body) VALUES (?, ?, ?)", (to, subject, body))
    db.commit()

def syndicate_mail(inviter, invitee):
    to = invitee+"@cam.ac.uk"
    subject = "Downing JCR Room Ballot"
    body = "Hello,\n\nThe user "+inviter+" has invited you to join their syndicate. To view the invitation, please click on the following link:\n\nhttps://ballot.downingjcr.co.uk/invite\n\nIf you have any questions, feel free to reply to this email."

    queue_email(to, subject, body)
