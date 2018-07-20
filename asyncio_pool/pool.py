# coding: utf8
'''Pool of asyncio coroutines with familiar interface'''

import traceback
import collections
import asyncio as aio


class AioPool(object):

    def __init__(self, size=1024, *, loop=None):
        self.loop = loop or aio.get_event_loop()

        self.size = size
        self._waiting = 0
        self._executed = 0
        self._joined = collections.deque()
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
        return 0 == self._waiting == self.n_active

    @property
    def is_full(self):
        return self.size <= self._waiting + self.n_active

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
            raise RuntimeError()  # TODO

        for fut in self._joined:
            if not fut.done():
                fut.set_result(True)

    async def _acquire(self):
        self._waiting += 1
        await self.semaphore.acquire()
        self._waiting -= 1

    async def _wrap(self, coro, future, cb=None, ctx=None):
        res, exc, tb = None, None, None

        try:
            res = await coro
            future.set_result(res)
        except Exception as exc:
            future.set_exception(exc)
            tb = traceback.format_exc()
        finally:
            self.semaphore.release()
            self._executed += 1

        try:
            if cb:
                await self.spawn(cb(res, (exc, tb), ctx))
        except Exception as exc_cb:
            pass  # TODO
        finally:
            if self.is_empty:
                self._release_joined()

    async def spawn(self, coro, cb=None, ctx=None):
        await self._acquire()
        future = self.loop.create_future()
        wrapped = self._wrap(coro, future, cb=cb, ctx=ctx)
        self.loop.create_task(wrapped)
        return future

    async def exec(self, coro):
        return await (await self.spawn(coro))

    async def itermap(self, fn, iterable):
        for it in iterable:
            yield (await self.spawn(fn(it)))

    async def map(self, fn, iterable, exc_as_result=True):
        futures = []
        async for fut in self.itermap(fn, iterable):
            futures.append(fut)
        await self.join()

        result = []
        for fut in futures:
            if fut.exception():
                res = fut.exception() if exc_as_result else None
            else:
                res = fut.result()
            result.append(res)
        return result
