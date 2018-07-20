# coding: utf8

import pytest
import asyncio as aio
from asyncio_pool import AioPool


async def wrk(n):
    await aio.sleep(1 / n)
    return n*10


@pytest.mark.asyncio
async def test_map_simple():
    task = range(1,11)
    pool = AioPool(size=7)
    res = await pool.map(wrk, task)
    assert res == [i*10 for i in task]


@pytest.mark.asyncio
async def test_map_crash():
    task = range(5)
    pool = AioPool(size=10)

    # exc as result
    res = await pool.map(wrk, task)
    assert isinstance(res[0], Exception)
    assert res[1:] == [i*10 for i in task[1:]]

    # None as result
    res = await pool.map(wrk, task, exc_as_result=False)
    assert res[0] is None
    assert res[1:] == [i*10 for i in task[1:]]
