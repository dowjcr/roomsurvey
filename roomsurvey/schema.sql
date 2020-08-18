DROP TABLE IF EXISTS meta;

CREATE TABLE meta (
	key TEXT UNIQUE PRIMARY KEY,
	value TEXT
);

INSERT INTO meta (key, value) VALUES ("version", "001");

DROP TABLE IF EXISTS syndicate;

CREATE TABLE syndicate (
	id INTEGER PRIMARY KEY,
	owner TEXT UNIQUE NOT NULL
);

DROP TABLE IF EXISTS user;

CREATE TABLE user (
	crsid TEXT UNIQUE PRIMARY KEY,
	syndicate INTEGER DEFAULT NULL,
	formtoken TEXT NOT NULL
);

DROP TABLE IF EXISTS syndicate_invitation;

CREATE TABLE syndicate_invitation (
	id INTEGER PRIMARY KEY,
	syndicate INTEGER NOT NULL,
	recipient TEXT NOT NULL,
	used INTEGER DEFAULT 0
);

DROP TABLE IF EXISTS log_message;

CREATE TABLE log_message (
	id INTEGER PRIMARY KEY,
	user TEXT NOT NULL,
	message TEXT NOT NULL
);

DROP TABLE IF EXISTS mail_queue;

CREATE TABLE mail_queue (
	id INTEGER PRIMARY KEY,
	recipient TEXT NOT NULL,
	subject TEXT NOT NULL,
	body TEXT NOT NULL
);
