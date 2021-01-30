from roomsurvey.db import get_db

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
