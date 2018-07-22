# coding: utf8

import os
import sys
curr_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.split(curr_dir)[0])

import itertools
import asyncio as aio
from asyncio_pool import AioPool
from async_timeout import timeout


async def worker(n):  # dummy worker
    await aio.sleep(1 / n)
    return n


async def spawn_n_usage(todo=[range(1,51), range(51,101), range(101,200)]):
    futures = []
    async with AioPool(size=20) as pool:
        for tasks in todo:
            for i in tasks:  # too many tasks
                # Returns quickly for all tasks, does not wait for pool space.
                # Workers are not spawned, they wait for pool space in their
                # own background tasks.
                fut = await pool.spawn_n(worker(i))
                futures.append(fut)
        # At this point not a single worker should start.

        # Context manager calls `join` at exit, so this will finish when all
        # workers return, crash or cancelled.

    assert sum(itertools.chain.from_iterable(todo)) == \
        sum(f.result() for f in futures)


async def spawn_usage(todo=range(1,4)):
    futures = []
    async with AioPool(size=2) as pool:
        for i in todo:  # 1, 2, 3
            # Returns quickly for 1 and 2, then waits for empty space for 3,
            # spawns 3 and returns. Can save some resources I guess.
            fut = await pool.spawn(worker(i))
            futures.append(fut)
        # At this point some of the workers already started.

        # Context manager calls `join()` at exit, so this will finish when all
        # workers return, crash or cancelled.

    assert sum(todo) == sum(fut.result() for fut in futures)  # all done


async def map_usage(todo=range(100)):
    pool = AioPool(size=10)
    # Joins internally, collects results from all spawned workers,
    # returns them in same order as `todo`, if worker crashes or cancelled:
    # returns exception object as a result.
    # Basically, it wraps `spawn_usage` code into one call.
    results = await pool.map(worker, todo)

    assert isinstance(results[0], ZeroDivisionError) \
        and sum(results[1:]) == sum(todo)


async def itermap_usage(todo=range(1,11)):
    # Python 3.6+
    result = 0
    async with AioPool(size=10) as pool:
        # Combines spawn_n and iterwait, which is a wrapper for asyncio.wait,
        # which yields results of finished workers according to `timeout` and
        # `yield_when` params passed to asyncio.wait (see it's docs for details)
        async for res in pool.itermap(worker, todo, timeout=0.5):
            result += res
        # technically, you can skip join call

    assert result == sum(todo)


async def callbacks_usage():
    pass  # TODO


async def details(todo=range(1,11)):
    pool = AioPool(size=5)

    # This code:
    f1 = []
    for i in todo:
        f1.append(await pool.spawn_n(worker(i)))
    # is equivalent to one call of `map_n`:
    f2 = await pool.map_n(worker, todo)

    # Afterwards you can await for any given future:
    try:
        assert 3 == await f1[2]  # result of spawn_n(worker(3))
    except Exception as e:
        # exception happened in worker (or CancelledError) will be re-raised
        pass

    # Or use `asyncio.wait` to handle results in batches (see `iterwait` also):
    important_res = 0
    more_important = [f1[1], f2[1], f2[2]]
    while more_important:
        done, more_important = await aio.wait(more_important, timeout=0.5)
        # handle result, note it will re-raise exceptions
        important_res += sum(f.result() for f in done)

    assert important_res == 2 + 2 + 3

    # But you need to join, to allow all spawned workers to finish
    # (of course you can `asyncio.wait` all of the futures if you want to)
    await pool.join()

    assert all(f.done() for f in itertools.chain(f1,f2))  # this is guaranteed
    assert 2 * sum(todo) == sum(f.result() for f in itertools.chain(f1,f2))


if __name__ == "__main__":
    aio.get_event_loop().run_until_complete(aio.gather(
        spawn_n_usage(),
        spawn_usage(),
        map_usage(),
        itermap_usage(),
        callbacks_usage(),
        details()
    ))
