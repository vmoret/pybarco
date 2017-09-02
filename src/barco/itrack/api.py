"""Provides API functions to load data from iTrack REST API."""
import json
from pkg_resources import resource_stream

from .proxy import ITrackProxy
from ..utils.pandas import to_dataframe, set_index, rename, to_datetime

# Load configuration file
_CONFIG = json.load(resource_stream(__name__, 'config.json'))


@to_datetime(_CONFIG['date_columns'])
@rename(columns=_CONFIG['columns'])
@set_index('key')
@to_dataframe
def search(jql, auth=None, server=None):
    """
    Returns a list with the data retrieved from iTrack REST API.

    Parameters
    ----------
    jql : unicode
        JQL query string -- this will be URL encoded
    auth : Auth tuple
        Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    server : TCPAddress
        TCPAddress tuple to define API ReST server.
    """
    retrieved = 0
    total = 1 # needs to be bigger than retrieved...

    # Initialize iTrack proxy
    proxy = ITrackProxy(auth=auth, server=server)

    # Search issues until all are retrieved
    while retrieved < total:
        items, total = proxy.search(jql, start_at=retrieved)
        retrieved += len(items)
        yield from iter(items)
