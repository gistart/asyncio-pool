# coding: utf8


def _get_future_result(future, exc_as_result=True):
    if future.exception():
        return future.exception() if exc_as_result else None
    else:
        return future.result()
