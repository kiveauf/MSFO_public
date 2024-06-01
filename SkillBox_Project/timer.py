import functools
import time
import typing

def async_def():
    def async_wrapper(func: typing.Callable) -> typing.Callable:
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                end = time.time()
                total = end - start
                print(f"{func} завершилась за {total} секунд")
        return wrapped
    return async_wrapper
