CREATE TABLE crawl (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	args TEXT,
	start_time DATETIME NOT NULL,
	end_time DATETIME
);
CREATE TABLE result (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	crawl_id INTEGER NOT NULL,
	crawl_url TEXT,
	error TEXT,
	page_url TEXT,
	script_url TEXT,
	script_domain TEXT,
	canvas BOOLEAN,
	canvas_id INTEGER,
	font_enum BOOLEAN,
	navigator_enum BOOLEAN,
	FOREIGN KEY(crawl_id) REFERENCES crawl(id),
	FOREIGN KEY(canvas_id) REFERENCES canvas(id)
);
CREATE TABLE property_count (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	result_id INTEGER NOT NULL,
	property TEXT,
	count INTEGER,
	FOREIGN KEY(result_id) REFERENCES result(id)
);
CREATE TABLE canvas (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	data_url TEXT NOT NULL UNIQUE
);
