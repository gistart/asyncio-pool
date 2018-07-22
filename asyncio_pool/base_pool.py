# coding: utf8
'''Pool of asyncio coroutines with familiar interface, python3.5+ friendly'''

import traceback
import collections
import asyncio as aio
from .utils import _get_future_result


class BaseAioPool(object):

    def __init__(self, size=1024, *, loop=None):
        self.loop = loop or aio.get_event_loop()

        self.size = size
        self._executed = 0
        self._joined = collections.deque()
        self._waiting = collections.deque()
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
        self._joined.append(fut)
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
        if not exc:
            future.set_result(res)
        else:
            future.set_exception(exc)

        if self.is_empty:
            self._release_joined()

    async def _spawn(self, future, coro, cb=None, ctx=None):
        try:
            await self.semaphore.acquire()
        except Exception as e:
            future.set_exception(e)
        self._waiting.remove(future)
        wrapped = self._wrap(coro, future, cb=cb, ctx=ctx)
        self.loop.create_task(wrapped)
        return future

    async def spawn_n(self, coro, cb=None, ctx=None):
        future = self.loop.create_future()
        self._waiting.append(future)
        self.loop.create_task(self._spawn(future, coro, cb=cb, ctx=ctx))
        return future

    async def spawn(self, coro, cb=None, ctx=None):
        future = self.loop.create_future()
        self._waiting.append(future)
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
        await self.join()

        results = []
        for fut in futures:
            res = _get_future_result(fut, exc_as_result)
            results.append(res)
        return results

    async def iterwait(self, *arg, **kw):  # TODO there's a way to support 3.5?
        raise NotImplementedError('python3.6+ required')

    async def itermap(self, *arg, **kw):  # TODO there's a way to support 3.5?
        raise NotImplementedError('python3.6+ required')
