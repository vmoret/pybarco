"""Utility function decorators."""
import datetime as dt
from functools import wraps


def join_with(string=' '):
    """Decorator factory to apply `str.join` on iterable result of `func`."""
    def _decorator(func):

        @wraps(func)
        def _wrapper(*args, **kwargs):
            return string.join(func(*args, **kwargs))
        return _wrapper
    return _decorator


def strptime_with(fmt=r'%Y-%m-%d', default=None):
    """Decorator factory to apply `datetime.strptime` on result of `func`."""
    def _decorator(func):

        @wraps(func)
        def _wrapper(*args, **kwargs):
            try:
                return dt.datetime.strptime(func(*args, **kwargs), fmt)
            except TypeError:
                return default
            except ValueError:
                return default
        return _wrapper
    return _decorator
