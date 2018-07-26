# coding: utf8


def result_noraise(future, exc_as_result=True):
    try:
        res = future.result()
        return res if exc_as_result else (res, None)
    except Exception as exc:
        # TODO traceback ??
        return exc if exc_as_result else (None, exc)
