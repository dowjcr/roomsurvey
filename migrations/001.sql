UPDATE meta SET value="002" WHERE key="version";

CREATE TABLE room (
	id INTEGER PRIMARY KEY,
	shortname TEXT UNIQUE NOT NULL,
	inhabitant TEXT DEFAULT NULL
);

CREATE TABLE review (
	id INTEGER PRIMARY KEY,
	author TEXT NOT NULL,
	room INTEGER NOT NULL,
	layout_rating INTEGER NOT NULL,
	facilities_rating INTEGER NOT NULL,
	noise_rating INTEGER NOT NULL,
	overall_rating INTEGER NOT NULL,
	title TEXT NOT NULL,
	body TEXT NOT NULL
);
