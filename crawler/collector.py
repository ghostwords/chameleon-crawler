#!/usr/bin/env python3

# chameleon-crawler
#
# Copyright 2015 ghostwords.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from time import sleep

from .utils import DATABASE_URL

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

        crawl_url, result = result

        if not result:
            with db:
                db['result'].insert(dict(
                    crawl_id=crawl_id,
                    crawl_url=crawl_url
                ))
            continue

        for page_url, page_data in result.items():
            for domain, ddata in page_data['domains'].items():
                for script_url, sdata in ddata['scripts'].items():
                    with db:
                        result_id = db['result'].insert(dict(
                            crawl_id=crawl_id,
                            crawl_url=crawl_url,
                            page_url=page_url,
                            domain=domain,
                            script_url=script_url,
                            canvas=sdata['canvas']['fingerprinting'],
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
