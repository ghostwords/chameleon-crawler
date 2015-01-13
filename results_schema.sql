CREATE TABLE IF NOT EXISTS crawl (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	start_time DATETIME NOT NULL,
	end_time DATETIME
);
CREATE TABLE IF NOT EXISTS result (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	crawl_id INTEGER NOT NULL,
	crawl_url TEXT,
	page_url TEXT,
	script_url TEXT,
	script_domain TEXT,
	canvas BOOLEAN,
	font_enum BOOLEAN,
	navigator_enum BOOLEAN,
    FOREIGN KEY(crawl_id) REFERENCES crawl(id)
);
CREATE TABLE IF NOT EXISTS property_count (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	result_id INTEGER NOT NULL,
	property TEXT,
	count INTEGER,
    FOREIGN KEY(result_id) REFERENCES result(id)
);
