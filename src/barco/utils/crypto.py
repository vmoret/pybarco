"""Provides cryptography classes and traits."""
from traitlets import HasTraits, TraitType
from cryptography.fernet import Fernet

class Cypher(TraitType):
    """A trait for cryptography cyphers."""

    default_value = Fernet(b'b0y2zCeZ7SH_S_hFOMd-8gZ-ed6S4MP_0GRNgG_mCRc=')
    info_text = 'a cryptography cypher isinstance'

    def validate(self, obj, value):
        """Check whether a given value is valid."""

        if hasattr(value, 'decrypt') and hasattr(value, 'encrypt'):
            return value
        self.error(obj, value)


class LightCypher(HasTraits):
    """A light cypher suite."""

    cypher = Cypher(Fernet(b'b0y2zCeZ7SH_S_hFOMd-8gZ-ed6S4MP_0GRNgG_mCRc='),
                    read_only=True)

    def encrypt(self, s, encoding='utf-8'):
        return self.cypher.encrypt(s.encode(encoding))

    def decrypt(self, token, encoding='utf-8'):
        return self.cypher.decrypt(token).decode(encoding)
