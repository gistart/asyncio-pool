# coding: utf8

import os
import sys
curr_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.split(curr_dir)[0])

import logging
import asyncio as aio
import json as myformat   # just for a demo


def parse_res(res):
    doc = myformat.loads(res)
    return doc.get('files') or [], doc.get('folders') or []


async def ls_cb(res, err, ctx):
    apipool, dbpool, api, db, log = ctx
    if err:
        log.error()
        return

    files, folders = parse_res(res)
    for folder in folders:
        await apipool.spawn(api.ls(folder['path']), cb=ls_cb, ctx=ctx)
        await dbpool.spawn(db.save(folder))
    for file in files:
        await dbpool.spawn(db.save(file))


async def example_ls():
    loop = aio.get_event_loop()
    api = await create_client(loop)
    db = await create_connection(dsn, loop)
    log = logging.getLogger('example_ls')

    with AioPool(size=10) as dbpool, \
            AioPool(size=10) as apipool:
        ctx = (apipool, dbpool, api, db, log)
        await apipool.spawn(api.ls('/'), cb=ls_cb, ctx=ctx)


if __name__ == "__main__":
    aio.get_event_loop().run_until_complete(example_ls())
