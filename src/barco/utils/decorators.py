"""Utility function decorators."""
import datetime as dt
from functools import wraps

from .recipes import isempty


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

def with_default(default, predicate=isempty):
    """
    Decorator factory to return a `default` value when applying `predicate`
    to wrapped return value is true.

    Parameters
    ----------
    default -- any
    predicate -- function
    """
    def _decorator(func):
        @wraps(func)
        def _wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            return default if res is None or predicate(res) else res
        return _wrapper
    return _decorator
