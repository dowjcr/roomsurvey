from roomsurvey.db import get_db
from roomsurvey.mail import syndicate_mail

def get_syndicate_for_user(crsid):
    db = get_db()
    syndicate = {}

    # Don't forget the trailing comma so that a tuple is passed to sqlite3, and not a string!
    syndicate_id = db.execute('SELECT syndicate FROM user WHERE crsid=?', (crsid,)).fetchone()

    if syndicate_id is None:
        return None
    if syndicate_id[0] is None:
        return None

    syndicate_data = db.execute('SELECT * FROM syndicate WHERE id=?', (syndicate_id[0],)).fetchone()
    syndicate["owner"] = syndicate_data["owner"]

    syndicate_others = db.execute('SELECT crsid FROM user WHERE syndicate=? AND crsid<>?', (syndicate_id[0], syndicate["owner"])).fetchall()
    syndicate["others"] = syndicate_others

    syndicate_invited = db.execute('SELECT recipient FROM syndicate_invitation WHERE used=0 AND syndicate=?', (syndicate_id[0],)).fetchall()
    syndicate["invited"] = syndicate_invited

    syndicate["complete"] = False if syndicate["invited"] else True

    return syndicate

def get_syndicate_invitations(crsid):
    db = get_db()

    invites = []

    invites_data = db.execute('SELECT syndicate_invitation.syndicate AS syndicate, syndicate.owner AS owner, syndicate_invitation.id AS id FROM syndicate_invitation, syndicate WHERE syndicate.id=syndicate_invitation.syndicate AND recipient=? AND syndicate_invitation.used=0', (crsid,)).fetchall()

    for invite in invites_data:
        invites.append({
            "id": invite["id"],
            "syndicate": invite["syndicate"],
            "owner": invite["owner"],
            "other_invites": db.execute('SELECT recipient FROM syndicate_invitation WHERE syndicate=? AND recipient<>?', (invite["syndicate"], crsid)).fetchall()
        })

    return invites

def update_invitation(crsid, accepted):
    # Assuming that there can only be one invitation at a time

    db = get_db()

    invite = get_syndicate_invitations(crsid)[0]
    syndicate = get_syndicate_for_user(crsid)

    if syndicate is not None:
        raise Exception("Trying to update an invitation for somebody who is already part of a syndicate")

    if accepted:
        db.execute('UPDATE user SET syndicate=? WHERE crsid=?', (invite["syndicate"], crsid))
    db.execute('UPDATE syndicate_invitation SET used=1 WHERE id=?', (invite["id"],))
    db.commit()

def create_syndicate(owner_crsid, invitees, want_to_stay):

    # NB `db` is a cursor here, so we can use `lastrowid`
    dbh = get_db()
    db = dbh.cursor()

    invitees.remove(owner_crsid)

    db.execute("INSERT INTO syndicate (owner, want_to_stay) VALUES (?, ?)", (owner_crsid, 1 if want_to_stay == "yes" else 0))
    syndicate_id = db.lastrowid

    db.execute("UPDATE user SET syndicate=? WHERE crsid=?", (syndicate_id, owner_crsid))

    for invitee in invitees:
        db.execute("INSERT INTO syndicate_invitation (syndicate, recipient) VALUES (?, ?)", (syndicate_id, invitee))
        syndicate_mail(owner_crsid, invitee)

    dbh.commit()
