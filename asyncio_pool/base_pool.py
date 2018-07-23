# coding: utf8
'''Pool of asyncio coroutines with familiar interface, python3.5+ friendly'''

import traceback
import collections
import asyncio as aio
from .utils import result_noraise


class BaseAioPool(object):
    ''' BaseAioPool implements features, supposed to work in all supported
    python versions. Other features supposed to be implemented as mixins.'''

    def __init__(self, size=1024, *, loop=None):
        self.loop = loop or aio.get_event_loop()

        self.size = size
        self._executed = 0
        self._joined = set()
        self._waiting = {}  # future -> task
        self._spawned = {}  # future -> task
        self.semaphore = aio.Semaphore(value=self.size, loop=self.loop)

    async def __aenter__(self):
        return self

    async def __aexit__(self, ext_type, exc, tb):
        await self.join()

    @property
    def n_active(self):
        return self.size - self.semaphore._value

    @property
    def is_empty(self):
        return 0 == len(self._waiting) == self.n_active

    @property
    def is_full(self):
        return self.size <= len(self._waiting) + self.n_active

    async def join(self):
        if self.is_empty:
            return True

        fut = self.loop.create_future()
        self._joined.add(fut)
        try:
            return await fut
        finally:
            self._joined.remove(fut)

    def _release_joined(self):
        if not self.is_empty:
            raise RuntimeError()  # TODO better message

        for fut in self._joined:
            if not fut.done():
                fut.set_result(True)

    async def _wrap(self, coro, future, cb=None, ctx=None):
        res, exc, tb = None, None, None
        try:
            res = await coro
        except Exception as _exc:
            exc = _exc
            tb = traceback.format_exc()  # TODO tb object instead of text
        finally:
            self._executed += 1

        if cb:
            err = None if exc is None else (exc, tb)
            wrapped = self._wrap(cb(res, err, ctx), future)
            self.loop.create_task(wrapped)
            return

        self.semaphore.release()

        if not future.done():
            if exc:
                future.set_exception(exc)
            else:
                future.set_result(res)

        del self._spawned[future]
        if self.is_empty:
            self._release_joined()

    async def _spawn(self, future, coro, cb=None, ctx=None):
        acq_error = False
        try:
            await self.semaphore.acquire()
        except Exception as e:
            acq_error = True
            if not future.done():
                future.set_exception(e)
        finally:
            del self._waiting[future]

        if future.done():
            if not acq_error and future.cancelled():  # outside action
                self.semaphore.release()
        else:  # all good, can spawn now
            wrapped = self._wrap(coro, future, cb=cb, ctx=ctx)
            task = self.loop.create_task(wrapped)
            self._spawned[future] = task
        return future

    async def spawn_n(self, coro, cb=None, ctx=None):
        future = self.loop.create_future()
        task = self.loop.create_task(self._spawn(future, coro, cb=cb, ctx=ctx))
        self._waiting[future] = task
        return future

    async def spawn(self, coro, cb=None, ctx=None):
        future = self.loop.create_future()
        self._waiting[future] = self.loop.create_future()  # TODO omg ???
        return await self._spawn(future, coro, cb=cb, ctx=ctx)

    async def exec(self, coro, cb=None, ctx=None):
        return await (await self.spawn(coro, cb=cb, ctx=ctx))

    async def map_n(self, fn, iterable):
        futures = []
        for it in iterable:
            fut = await self.spawn_n(fn(it))
            futures.append(fut)
        return futures

    async def map(self, fn, iterable, exc_as_result=True):
        futures = await self.map_n(fn, iterable)
        await aio.wait(futures)
        return [result_noraise(fut, exc_as_result) for fut in futures]

    async def iterwait(self, *arg, **kw):  # TODO there's a way to support 3.5?
        raise NotImplementedError('python3.6+ required')

    async def itermap(self, *arg, **kw):  # TODO there's a way to support 3.5?
        raise NotImplementedError('python3.6+ required')

    def _cancel(self, *futures):
        tasks, _futures = [], []

        if not len(futures):  # meaning cancel all
            tasks.extend(self._waiting.values())
            tasks.extend(self._spawned.values())
            _futures.extend(self._waiting.keys())
            _futures.extend(self._spawned.keys())
        else:
            for fut in futures:
                task = self._spawned.get(fut, self._waiting.get(fut))
                if task:
                    tasks.append(task)
                    _futures.append(fut)

        cancelled = sum([1 for fut in tasks if fut.cancel()])
        return cancelled, _futures

    async def cancel(self, *futures, exc_as_result=True):
        cancelled, _futures = self._cancel(*futures)
        await aio.sleep(0)  # let them actually cancel
        # need to collect them anyway, to supress warnings
        results = [result_noraise(fut, exc_as_result) for fut in _futures]
        return cancelled, results
