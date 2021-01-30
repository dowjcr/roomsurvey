# Downing JCR Room Ballot Survey

This system was developed in order to facilitate the collection of syndicate and room preference information during the re-run of the room ballot due to COVID-19, in conjunction with Matt Moore's room selection algorithm. As such, it was written very quickly to meet a tight deadline and might benefit from some improvements if used again.

## Installation

You probably want to do this with a `virtualenv`. For a simple development environment:

```
$ python3 -m venv venv
$ . venv/bin/activate
(venv) $ pip3 install -r requirements.txt
(venv) $ FLASK_APP=roomsurvey flask run
```

You can set up the database with the `init-db` command, but currently you might need to apply migrations
from the `migrations` directory to make sure you have the latest schema. One day I might fix this and make
it a bit more convenient.

## Built with

  * [Flask](https://flask.palletsprojects.com/en/1.1.x/)
  * [python-ucam-webauth](https://python-ucam-webauth.readthedocs.io/en/latest/index.html)
  * [Bootstrap](https://getbootstrap.com)
  * [SQLite](https://sqlite.org)

## Author

Lawrence Brown, JCR Internet Officer 2019/20

## License

MIT, please see the `LICENSE` file for more information.
