#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2016 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from time import sleep

from utils.database import DATABASE_URL

import dataset


def collect(crawl_id, result_queue, log):
    db = dataset.connect(DATABASE_URL)

    while True:
        if result_queue.empty():
            sleep(0.01)
            continue

        result = result_queue.get()

        if result is None:
            break

        crawl_url, error, result = result

        if not result:
            with db:
                db['result'].insert(dict(
                    crawl_id=crawl_id,
                    crawl_url=crawl_url,
                    error=error
                ))
            continue

        for page_url, page_data in result.items():
            if not page_data['domains']:
                # nothing found
                with db:
                    db['result'].insert(dict(
                        crawl_id=crawl_id,
                        crawl_url=crawl_url,
                        page_url=page_url
                    ))
                continue

            for script_domain, ddata in page_data['domains'].items():
                for script_url, sdata in ddata['scripts'].items():
                    with db:
                        canvas_id = None
                        if 'dataURL' in sdata['canvas']:
                            data_url = sdata['canvas']['dataURL']
                            if data_url:
                                db.query("""INSERT OR IGNORE INTO canvas (data_url)
                                    VALUES (:data_url)""", data_url=data_url)
                                canvas_id = db['canvas'].find_one(
                                    data_url=data_url)['id']

                        result_id = db['result'].insert(dict(
                            crawl_id=crawl_id,
                            crawl_url=crawl_url,
                            page_url=page_url,
                            script_url=script_url,
                            script_domain=script_domain,
                            canvas=sdata['canvas']['fingerprinting'],
                            canvas_id=canvas_id,
                            font_enum=sdata['fontEnumeration'],
                            navigator_enum=sdata['navigatorEnumeration']
                        ))

                    # property access counts get saved in `property_count`
                    rows = []
                    for property, count in sdata['counts'].items():
                        rows.append(dict(
                            result_id=result_id,
                            property=property,
                            count=count
                        ))
                    with db:
                        db['property_count'].insert_many(rows)

    log("Collecting finished.")
