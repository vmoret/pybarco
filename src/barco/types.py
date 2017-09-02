"""Provides trait types"""

from traitlets import TraitType


class Auth(TraitType):
    """A trait for a Basic/Digest/Custom HTTP Auth tuple."""

    default_value = ('', '')
    info_text = 'an (user, password) tuple'

    def validate(self, obj, value):
        """Check whether a given value is valid."""
        if isinstance(value, tuple):
            if len(value) == 2:
                if isinstance(value[0], str) and isinstance(value[1], str):
                    return value
        self.error(obj, value)
