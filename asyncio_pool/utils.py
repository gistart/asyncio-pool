# coding: utf8

import asyncio as aio


def result_noraise(future, exc_as_result=True):
    try:
        return future.result()
    except Exception as exc:
        return exc if exc_as_result else None
