# asyncio-pool

TODO: cancelled, timeouts, callbacks, features, tests, readme

Example (more in `tests/` and `examples/` dirs): # TODO

```python
import asyncio as aio
from asyncio_pool import AioPool


async def worker(n):
    await aio.sleep(1 / n)


async def run_in_pool():

    async with AioPool(size=10) as pool:  # no more than 10 concurrent coroutines
        results = await pool.map(worker, range(1, 100))

### OR

    pool = AioPool(size=10)

    # generator returning futures for each worker result
    futures = await pool.itermap(worker, range(1,100))
    # or spawning manually: list of futures for each worker result
    futures = [await pool.spawn(worker(i)) for i in range(1,100)]

    await pool.join()
    print [fut.result() for fut in batch]  # will re-raise exceptions


### OR moar later
```
