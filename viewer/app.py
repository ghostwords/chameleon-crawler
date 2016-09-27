#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2016 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from datetime import datetime
from flask import Flask, render_template, request
from utils.database import DATABASE_URL, initialize_database

import dataset


app = Flask(__name__)

app.config['DATABASE_URL'] = DATABASE_URL
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

initialize_database()


def get_canvases(result_ids):
    canvases = {}

    sql = """SELECT canvas.id, data_url
        FROM canvas
        JOIN result ON result.canvas_id = canvas.id
        WHERE result.id IN (%s)""" % ','.join(
        [str(int(id)) for id in result_ids])

    with dataset.connect(app.config['DATABASE_URL']) as db:
        for row in db.query(sql):
            canvases[row['id']] = row['data_url']

    return canvases


def get_fingerprinters(crawl_ids=None, canvas=True, font_enum=True,
        navigator_enum=True, num_properties=4, webgl=False, webrtc=False):
    fp = {}
    result_ids = set()

    in_clause = ""
    if crawl_ids:
        in_clause = "AND crawl_id IN (%s)" % ','.join(
            [str(int(id)) for id in crawl_ids])

    filters = []
    if canvas:
        filters.append("canvas = 1")
    if font_enum:
        filters.append("font_enum = 1")
    if navigator_enum:
        filters.append("navigator_enum = 1")
    if num_properties:
        filters.append("num_properties >= %s" % str(int(num_properties)))

    having_clause = ""
    if filters:
        having_clause = "HAVING %s" % " OR ".join(filters)

    where = []
    if webgl:
        where.append("""(
            pc.property = 'WebGLRenderingContext.prototype.getParameter'
                OR pc.property =
                    'WebGLRenderingContext.prototype.getSupportedExtensions'
            )""")
    if webrtc:
        where.append("""(
            pc.property = 'RTCPeerConnection'
                OR pc.property = 'webkitRTCPeerConnection'
            )""")

    union_clause = ""
    if where and filters:
        union_clause = """UNION
            SELECT
                result.*,
                COUNT(pc.result_id) num_properties
            FROM result
            JOIN property_count pc ON pc.result_id = result.id
            WHERE %s
            GROUP BY pc.result_id""" % " OR ".join(where)
    elif where and not filters:
        in_clause = "%s AND (%s)" % (in_clause, " OR ".join(where))

    sql = """SELECT * FROM (
        SELECT
            result.*,
            COUNT(pc.result_id) num_properties
        FROM result
        LEFT JOIN property_count pc ON pc.result_id = result.id
        WHERE 1 {in_clause}
        GROUP BY COALESCE(pc.result_id, result.id)
        {having_clause}
        {union_clause}
    ) GROUP BY
        crawl_url,
        page_url,
        script_url,
        canvas,
        canvas_id,
        font_enum,
        navigator_enum,
        num_properties""".format(
        in_clause=in_clause,
        having_clause=having_clause,
        union_clause=union_clause)

    with dataset.connect(app.config['DATABASE_URL']) as db:
        result = db.query(sql)

        """ {
            row['script_domain']: {
                row['script_url']: [
                    row,
                    ...
                ],
                ...
            },
            ...
        }"""
        for row in result:
            fp.setdefault(row['script_domain'], {}).setdefault(
                row['script_url'], []).append(row)

            result_ids.add(row['id'])

    return fp, result_ids


def get_problem_pages(crawl_ids):
    if crawl_ids:
        in_clause = "AND crawl_id IN (%s)" % ','.join(
            [str(int(id)) for id in crawl_ids])

    sql = """SELECT crawl_url, error, COUNT(*) count
        FROM result
        WHERE error IS NOT NULL %s
        GROUP BY crawl_url, error
        ORDER BY count DESC""" % (in_clause if crawl_ids else "")

    with dataset.connect(app.config['DATABASE_URL']) as db:
        result = db.query(sql)
        return list(result)


def get_error_counts():
    errors = {}

    with dataset.connect(app.config['DATABASE_URL']) as db:
        result = db.query(
            """SELECT crawl_id, error, COUNT(DISTINCT crawl_url) num_urls
            FROM result
            WHERE error IS NOT NULL
            GROUP BY crawl_id, error"""
        )

        for row in result:
            errors.setdefault(
                row['crawl_id'], {})[row['error']] = row['num_urls']

    return errors


def get_crawls():
    with dataset.connect(app.config['DATABASE_URL']) as db:
        return list(db.query(
            """SELECT
            crawl.id,
            crawl.args,
            COUNT(DISTINCT crawl_url) num_urls,
            (STRFTIME('%s', end_time) - STRFTIME('%s', start_time)) duration,
            STRFTIME('%s', start_time) start_time
            FROM crawl
            JOIN result ON result.crawl_id = crawl.id
            GROUP BY crawl.id
            ORDER BY crawl.id DESC"""
        ))


@app.template_filter('number_format')
def number_format(value):
    return '{:,}'.format(value)


@app.route('/errors')
def errors():
    crawl_ids = [int(i) for i in request.args.getlist('crawl')]

    return render_template(
        'errors.html',
        problem_pages=get_problem_pages(crawl_ids)
    )


@app.route('/results')
def results():
    args = {}

    crawl_ids = [int(i) for i in request.args.getlist('crawl')]

    if crawl_ids:
        args['crawl_ids'] = crawl_ids

    all_filters = {
        'canvas',
        'font_enum',
        'navigator_enum',
        'num_properties',
        'webgl',
        'webrtc'
    }
    filters = request.args.getlist('filter')

    if set.intersection(all_filters, filters):
        for filt in all_filters:
            args[filt] = filt in filters

        if 'num_properties' in filters:
            args['num_properties'] = request.args.get('num_properties')

    fingerprinters, result_ids = get_fingerprinters(**args)

    return render_template(
        'results.html',
        fingerprinters=fingerprinters,
        canvases=get_canvases(result_ids)
    )


@app.route('/')
def index():
    crawls = get_crawls()

    for crawl in crawls:
        crawl['start_time'] = datetime.utcfromtimestamp(
            int(crawl['start_time'])).strftime("%b %d %Y %I:%M %p")

    return render_template(
        'crawls.html',
        crawls=crawls,
        error_counts=get_error_counts()
    )
