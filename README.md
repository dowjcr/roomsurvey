# Downing JCR Room Ballot Survey

**This branch is for the 2021 room ballot. The database schema is not compatible with previous versions.**
The 2020 codebase lives on in the `2020` branch.

This web-app facilitates the collection of syndicate and room preference information, which can be passed
to Matt Moore's room selection algorithm.

## Installation

You probably want to do this with a `virtualenv`. For a simple development environment:

```
$ python3 -m venv venv
$ . env.sh
(venv) $ pip3 install -r requirements.txt
(venv) $ mkdir instance
(venv) $ cp config.default.py instance/config.py
(venv) $ flask init-db
(venv) $ flask import-users
(venv) $ flask run
```

 * `init-db` initialises the database according to `roomsurvey/schema.sql`.
 * `import-users` imports the `users.csv` file into the database. This file can be generated using the
 [ucam-lookup-byyear](https://github.com/dowjcr/ucam-lookup-byyear) script.
 * `import-allocations` imports room allocation data from the `allocations.csv` file produced by the room
 selection program. This is required in order to get room reviews.
 * `send-review-reminder` queues an email to be sent to everyone who has been allocated a room. See
 `roomsurvey/mail.py` for more information.
 * `send-emails` sends any queued emails, and should be run by cron in production. Only sending via the local
 mail server is supported at the moment.

All the routes of the web-app are defined in `roomsurvey/__init__.py`. Reading this file will give you a
quick overview of the app's architecture.

**Hint**: you might want to take note of who has permission to read `instance/db.sqlite` and
`instance/config.py`. These files tend to contain sensitive information in production.

## Built with

  * [Flask](https://flask.palletsprojects.com)
  * [python-ucam-webauth](https://python-ucam-webauth.readthedocs.io/en/latest/index.html)
  * [Bootstrap](https://getbootstrap.com)
  * [SQLite](https://sqlite.org)

## Author

Lawrence Brown, JCR Internet Officer 2020/21

## License

MIT, please see the `LICENSE` file for more information.
