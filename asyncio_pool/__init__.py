# coding: utf8

import sys

from .utils import result_noraise
from .base_pool import BaseAioPool


if sys.version_info < (3, 6):  # this means 3.5  # TODO test 3.4?

    class AioPool(BaseAioPool): pass

else:
    from .mx_asyncgen import MxAsyncGenPool, iterwait

    class AioPool(MxAsyncGenPool, BaseAioPool): pass
