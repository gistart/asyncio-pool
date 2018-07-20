# coding: utf8

from .asyncio_pool import AioPool


async def test(n):
    print('<<', n)
    n = n * 10
    await aio.sleep(1)
    print('>>', n, 'done')
    return n


async def test_spawn(loop):
    pool = AioPool(2, loop=loop)

    results = []
    for i in range(1,8):
        res = await pool.spawn(test(i), test)
        results.append(res)
    await pool.join()
    print([r.result() for r in results])


async def test_exec(loop):
    pool = AioPool(2, loop=loop)
    await pool.spawn(test(1))
    print('<<<<<<<', await pool.exec(test(2)))
    await pool.join()


async def test_itermap(loop):
    futures = []
    async with AioPool(size=2, loop=loop) as pool:
        async for fut in pool.itermap(test, range(1,4)):
            futures.append(fut)
    print([f.result() for f in futures])


async def test_map(loop):
    pool = AioPool(2, loop=loop)
    print(await pool.map(test, range(1,6)))
    print(await pool.map(test, [(i,i+1) for i in range(10)]))


async def test_context(loop):
    futures = []
    async with AioPool(2, loop=loop) as pool:
        for i in range(1,6):
            fut = await pool.spawn(test(i))
            futures.append(fut)

    print([r.result() for r in futures])


if __name__ == "__main__":
    loop = aio.get_event_loop()

    loop.run_until_complete(test_spawn(loop))
    loop.run_until_complete(test_exec(loop))
    loop.run_until_complete(test_context(loop))
    loop.run_until_complete(test_itermap(loop))
    loop.run_until_complete(test_map(loop))
