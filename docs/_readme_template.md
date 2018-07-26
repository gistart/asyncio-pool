# asyncio-pool

Pool of asyncio coroutines with familiar interface. Supports python 3.5+ (including PyPy 6+, which is also 3.5 atm)

AioPool makes sure _no more_ and _no less_ (if possible) than `size` spawned coroutines are active at the same time. _spawned_ means created and scheduled with one of the pool interface methods, _active_ means coroutine function started executing it's code, as opposed to _waiting_ -- which waits for pool space without entering coroutine function.

## Interface

Read [code doctrings](../master/asyncio_pool/base_pool.py) for details.

#### AioPool(size=4, *, loop=None)

Creates pool of `size` concurrent tasks. Supports async context manager interface.

#### spawn(coro, cb=None, ctx=None)

Waits for pool space, then creates task for `coro` coroutine, returning future for it's result. Can spawn coroutine, created by `cb` with result of `coro` as first argument. `ctx` context is passed to callback as third positinal argument.

#### exec(coro, cb=None, ctx=None)

Waits for pool space, then creates task for `coro`, then waits for it to finish, then returns result of `coro` if no callback is provided, otherwise creates task for callback, waits for it and returns result of callback.

#### spawn_n(coro, cb=None, ctx=None)

Creates waiting task for `coro`, returns future without waiting for pool space. Task is executed "in pool" when pool space is available.

#### join()

Waits for all spawned (active and waiting) tasks to finish. Joining pool from coroutine, spawned by the same pool leads to *deadlock*.

#### cancel(*futures)

Cancels spawned tasks (active and waiting), finding them by provided `futures`. If no futures provided -- cancels all spawned tasks.

#### map(fn, iterable, cb=None, ctx=None, *, get_result=getres.flat)

Spawns coroutines created by `fn` function for each item in `iterable` with `spawn`, waits for all of them to finish (including callbacks), returns results maintaining order of `iterable`.

#### map_n(fn, iterable, cb=None, ctx=None, *, get_result=getres.flat)

Spawns coroutines created by `fn` function for each item in `iterable` with `spawn_n`, returns futures for task results maintaining order of `iterable`.

#### itermap(fn, iterable, cb=None, ctx=None, *, flat=True, get_result=getres.flat, timeout=None, yield_when=asyncio.ALL_COMPLETED)

Spawns tasks with `map_n(fn, iterable, cb, ctx)`, then waits for results with `asyncio.wait` function, yielding ready results one by one if `flat` == True, otherwise yielding list of ready results.



## Usage

`spawn` and `map` methods is probably what you should use in 99% of cases. Their overhead is minimal (~3% execution time), and even in worst cases memory usage is insignificant.

`spawn_n`, `map_n` and `itermap` methods give you more control and flexibily, but they come with a price of higher overhead. They spawn all tasks that you want, and most of the tasks wait their turn "in background". If you spawn too much (10**6+ tasks) -- you'll use most of the memory you have in system, also you'll lose a lot of time on "concurrency management" of all the tasks spawned.

Play with `python tests/loadtest.py -h` to understand what you want to use.

Usage examples (more in [tests/](../master/tests/) and [examples/](../master/examples/)):

```python
{tmpl_usage_examples}
```
