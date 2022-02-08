# Downing JCR Room Ballot Survey

**This branch is for the 2022 room ballot.**
The 2021/20 codebases live on in the `2021` and the `2020` branches respectively.

In previous years, the JCR has collected syndicates and room preference data. However, as of 2022,
we agreed that the College should be responsible for collecting data, for privary purposes. This
site therefore acts as an information hub regarding the ballot, including:
 - key links
 - room allocations
 - information about how the ballot algorithm is run

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
 * `send-survey-reminder` queues an email to be sent to everyone who is part of syndicate in which one or more
 member(s) has not completed the preferences form. (good for peer pressure)
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
