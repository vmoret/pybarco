"""Provides commonly used pandas related utility and decorator functions."""
from datetime import datetime
import functools
import numpy as np
import pandas as pd


def to_dataframe(func):
    """Converts the result of `func` to a pandas DataFrame."""

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        return pd.DataFrame(func(*args, **kwargs))
    return _wrapper


def set_index(keys, **kws):
    """
    Set the DataFrame index (row labels) using one or more existing columns.

    Parameters
    ----------
    keys -- unicode or list
        column label or list of column labels / arrays
    """

    def _decorator(func):

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            obj = func(*args, **kwargs)
            if isinstance(obj, pd.DataFrame):
                return obj.set_index(keys, **kws)
            return obj

        return _wrapper
    return _decorator


def rename(index=None, columns=None, **kws):
    """
    Alter axes input function of functions. Function / dict values must be
    unique (1-to-1). Labels not contained in dict / Series will be left as-is.
    Extra labels listed don't throw an error.

    Parameters
    ----------
    index, columns -- dict-like or function, optional
        dict-like or functions are transformations to apply to that axis' value
    """

    def _decorator(func):

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            obj = func(*args, **kwargs)
            if isinstance(obj, pd.DataFrame):
                return obj.rename(index=index, columns=columns, **kws)
            return obj

        return _wrapper
    return _decorator


def to_datetime(columns, **kws):
    """
    Alter axes input function of functions. Function / dict values must be
    unique (1-to-1). Labels not contained in dict / Series will be left as-is.
    Extra labels listed don't throw an error.

    Parameters
    ----------
    index, columns -- dict-like or function, optional
        dict-like or functions are transformations to apply to that axis' value
    """
    def _decorator(func):

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            obj = func(*args, **kwargs)
            if isinstance(obj, pd.DataFrame):
                return obj.assign(**{
                    column: lambda df, col=column: pd.to_datetime(df[col], **kws)
                    for column in columns
                })
            return obj

        return _wrapper
    return _decorator


def categorize(columns):
    """
    Decorator factory that changes types of `columns` of result value
    to pandas categories when result value is a pandas.DataFrame.

    Parameters
    ----------
    columns -- list
        Name of the columns to change type to category.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            if isinstance(res, pd.DataFrame):
                return res.assign(**{k: lambda df, k=k: pd.Categorical(df[k])
                                     for k in columns})
            return res
        return wrapper
    return decorator


def busday_counter(start, end=None, default=datetime.today()):
    """
    Generates a busday counter for `start` and `end` date column that can be
    applied to a pandas DataFrame.

    Parameters
    ----------
    start, end -- str
        column names of the pandas DataFrame
    default -- datetime
        The fallback date/time to be used when start or end columns are not
        available in the pandas DataFrame.
        Also used to replace NaN values in the end column.
    """
    def inner(df):
        columns = df.columns.tolist()
        return np.busday_count(
            df[start].tolist() if start in columns else default,
            df[end].fillna(default).tolist() if end in columns else default
        )
    return inner
