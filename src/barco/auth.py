import os

from .utils.crypto import LightCypher

class BasicAuth(tuple):

    @classmethod
    def from_env(cls, key):
        user = os.getenv(key + '_USER', '')
        token = os.getenv(key + '_PASSWORD', '').encode('utf-8')
        password = LightCypher().decrypt(token)
        return cls([user, password])

    def __repr__(self):
        user, password = self
        token = LightCypher().encrypt(password)
        return '<BasicAuth {} {}>'.format(user, token.decode('utf-8'))
