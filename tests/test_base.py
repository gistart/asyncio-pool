# coding: utf8

import pytest
import asyncio as aio
from asyncio_pool import AioPool
from async_timeout import timeout


@pytest.mark.asyncio
async def test_timeout_cancel():
    async def wrk(sem):
        async with sem:
            await aio.sleep(1)

    sem = aio.Semaphore(value=2)

    async with timeout(0.2):
        with pytest.raises(aio.CancelledError):
            await aio.gather(*[wrk(sem) for _ in range(3)])


@pytest.mark.asyncio
async def test_outer_join():

    todo, to_release = range(1,15), range(10)
    done, released = [], []

    async def inner(n):
        nonlocal done
        await aio.sleep(1 / n)
        done.append(n)

    async def outer(n, pool):
        nonlocal released
        await pool.join()
        released.append(n)

    loop = aio.get_event_loop()
    pool = AioPool(size=100)

    tasks = [await pool.spawn(inner(i)) for i in todo]
    joined = [loop.create_task(outer(j, pool)) for j in to_release]
    await pool.join()

    assert len(released) < len(to_release)
    await aio.wait(joined)
    assert len(todo) == len(done) and len(released) == len(to_release)


@pytest.mark.asyncio
async def test_internal_join():
    async def wrk(n, pool):
        aio.sleep(1 / n)
        if n == 3:
            await pool.join()
        else:
            await pool.spawn(wrk(n + 1, pool))
        return n

    return True
    pool = AioPool(size=3)
    await pool.spawn(wrk(1, pool))

    async with timeout(1.5) as tm:
        await pool.join()

    assert tm.expired
