#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2016 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import dataset

DATABASE_URL = 'sqlite:///results.sqlite3'
SCHEMA_VERSION = 3

MIGRATIONS = {
    2: ["ALTER TABLE crawl ADD COLUMN args TEXT"],
    3: [
        (
            "CREATE TABLE canvas ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "data_url TEXT NOT NULL UNIQUE"
            ")"
        ),
        "ALTER TABLE result ADD COLUMN canvas_id INTEGER REFERENCES canvas(id)"
    ]
}


def migrate_database(current_version):
    # TODO in a transaction, BUT pysqlite doesn't do DDL transactions correctly
    # http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#transactional-ddl
    with dataset.connect(DATABASE_URL) as db:
        for i in range(current_version + 1, SCHEMA_VERSION + 1):
            for sql in MIGRATIONS[i]:
                db.query(sql)


def initialize_database():
    # in a transaction
    with dataset.connect(DATABASE_URL) as db:
        current_version = next(db.query("PRAGMA user_version"))['user_version']

        if current_version == 0:
            # new database: create tables from schema
            if 'crawl' not in db.tables:
                with open('results_schema.sql') as f:
                    for sql in f.read().split(';'):
                        db.query(sql)

            # "version 1" database: existing db from before versioning
            else:
                migrate_database(1)

        # existing database: apply schema updates
        elif current_version != SCHEMA_VERSION:
            migrate_database(current_version)

        if current_version != SCHEMA_VERSION:
            db.query("PRAGMA user_version = %i" % SCHEMA_VERSION)
