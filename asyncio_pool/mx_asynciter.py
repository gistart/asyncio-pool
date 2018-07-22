# coding: utf8
'''Mixin for BaseAioPool with async iterator features python3.6+'''

import asyncio as aio
from .utils import _get_future_result


class MxAsyncIterPool(object):

    async def iterwait(self, futures, *, flat=True, exc_as_result=True,
            timeout=None, yield_when=aio.ALL_COMPLETED):

        _futures = futures[:]
        while _futures:
            done, _futures = await aio.wait(_futures, loop=self.loop,
                    timeout=timeout, return_when=yield_when)
            if flat:
                for fut in done:
                    yield _get_future_result(fut, exc_as_result)
            else:
                yield [_get_future_result(f, exc_as_result) for f in done]

    async def itermap(self, fn, iterable, *, flat=True, exc_as_result=True,
            timeout=None, yield_when=aio.ALL_COMPLETED):

        futures = await self.map_n(fn, iterable)
        generator = self.iterwait(futures, flat=flat, timeout=timeout,
                exc_as_result=exc_as_result, yield_when=yield_when)
        async for batch in generator:
            yield batch  # TODO is it possible to return a generator?
