''' typing stub for asyncio-pool '''

import asyncio
from typing import (
    Any, AsyncGenerator, Callable, Coroutine, Dict,
    Iterable, List, Optional, Set, Tuple, Union
)


__all__ = ['getres', 'AioPool']


class getres:
    dont: Callable
    flat: Callable
    pair: Callable


class AioPool(object):
    def __init__(self, size: int = 1024, *, loop: Optional[asyncio.AbstractEventLoop] = None) -> None: ...

    async def __aenter__(self) -> AioPool: ...

    async def __aexit__(self, ext_type, exc, tb) -> None: ...

    def __len__(self) -> int: ...

    def n_active(self) -> int: ...

    def is_empty(self) -> bool: ...

    def is_full(self) -> bool: ...

    async def join(self) -> bool: ...

    def _release_joined(self) -> None: ...

    def _build_callback(
        self,
        cb: Callable,
        res: Any,
        err: Optional[Tuple] = None,
        ctx: Optional[Tuple] = None
    ) -> Tuple[Optional[Coroutine], Optional[Exception]]: ...

    async def _wrap(
        self,
        coro: Coroutine,
        future: asyncio.Future,
        cb: Optional[Callable] = None,
        ctx: Optional[Tuple] = None
    ) -> None: ...

    async def _spawn(
        self,
        future: asyncio.Future,
        coro: Coroutine,
        cb: Optional[Callable] = None,
        ctx: Optional[Tuple] = None
    ) -> asyncio.Future: ...

    async def spawn(
        self,
        coro: Coroutine,
        cb: Optional[Callable] = None,
        ctx: Optional[Tuple] = None
    ) -> asyncio.Future: ...

    def spawn_n(
        self,
        coro: Coroutine,
        cb: Optional[Callable] = None,
        ctx: Optional[Tuple] = None
    ) -> asyncio.Future: ...

    async def exec(
        self,
        coro: Coroutine,
        cb: Optional[Callable] = None,
        ctx: Optional[Tuple] = None
    ) -> Any: ...

    def map_n(
        self,
        fn: Callable,
        iterable: Iterable,
        cb: Optional[Callable] = None,
        ctx: Optional[Tuple] = None
    ) -> List[asyncio.Future]: ...

    async def map(
        self,
        fn: Callable,
        iterable: Iterable,
        cb: Optional[Callable] = None,
        ctx: Optional[Tuple] = None,
        *,
        get_result: Callable = getres.flat
    ) -> List[Any]: ...

    def itermap(
        self,
        fn: Callable,
        iterable: Iterable,
        cb: Optional[Callable] = None,
        ctx: Optional[Tuple] = None,
        *,
        flat: bool = True,
        get_result: Callable = getres.flat,
        timeout: Optional[int] = None,
        yield_when: str = asyncio.ALL_COMPLETED
    ) -> AsyncGenerator[Any, None]: ...

    async def cancel(
        self,
        *futures: asyncio.Future,
        get_result: Callable = getres.flat
    ) -> Tuple[int, List[Any]]: ...


def _get_loop() -> asyncio.AbstractEventLoop: ...
