"""Python recipes."""
from functools import reduce, partial
import re

splitstr = partial(str.split, sep=' ')


def nth(sequence, n=1):
    """Returns the `n`th element from `sequence`.

    >>> nth([1, 2])
    1
    >>> nth([1, 2], n=2)
    2
    """
    return sequence[n - 1]


def fst(sequence):
    """Returns first element from `sequence`.

    >>> fst([1, 2])
    1
    """
    return sequence[0]

def compose(*funcs):
    """Returns composed function of `funcs`."""
    first, *rest = funcs

    def _apply(arg, func):
        return func(arg)

    def _inner(*args, **kwargs):
        return reduce(_apply, rest, first(*args, **kwargs))

    return _inner


def ident(value):
    """Returns `value`.

    >>> ident(10)
    10
    """
    return value

def const(value):
    """Returns `value`.

    >>> const(100)(20)
    100
    """
    def _inner(*args, **kwargs):
        return value
    return _inner


def itemgetter(item, default=None):
    """Returns an itemgetter which allows for a `default` value when
    `item` was not present in mapping.

    >>> get_foo = itemgetter('foo', default=0)
    >>> get_foo(dict(foo=10))
    10
    >>> get_foo(dict(bar=10))
    0
    """

    def _inner(obj):
        return obj.get(item, default) if hasattr(obj, 'get') else default
    return _inner


def snake_case(string):
    """Converts CamelCase `string` to snake_case."""
    return re.sub(
        '([a-z0-9])([A-Z])', r'\1_\2',
        re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    ).lower()


def bool2int(value):
    """Returns the integer representation of a boolean `value`."""
    return 1 if value else 0
