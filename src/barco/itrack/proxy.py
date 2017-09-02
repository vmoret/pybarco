"""Provides functions to load data from iTrack REST API."""
import urllib
import logging
import functools
from collections import Mapping

import requests
from traitlets import HasTraits, TCPAddress

from ..types import Auth
from .parser import parse_itrack_issue

# URL format string for `search` queries
_SEARCH = 'https://{}:{:d}/rest/api/2/search?jql={}&startAt={:d}&maxResults={:d}'

# Logger instance
_logger = logging.getLogger(__name__)


def parse_itrack_issues(func):
    """
    Converts the raw JSON object resulting from `func` to a list of iTrack issue
    mappings.

    Parameters
    ----------
    func : function
        A function that returns a raw JSON object.
    """

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        obj = func(*args, **kwargs)

        if isinstance(obj, Mapping):
            issues = [parse_itrack_issue(issue)
                      for issue in obj.get('issues', [])]
            total = int(obj.get('total', 0))
            return issues, total

        return [], 0

    return _wrapper


class ITrackProxy(HasTraits):
    """A proxy to the iTrack ReST API."""

    server = TCPAddress(help='TCP address of the ReST API server')
    auth = Auth(help='Auth tuple to enable Basic/Digest/Custom HTTP Auth.')

    @parse_itrack_issues
    def search(self, jql, start_at=0, max_results=500):
        """
        Returns a JSON object with data retrieved from iTrack REST API.

        Parameters
        ----------
        jql : unicode
            JQL query string -- this will be URL encoded
        start_at : int
            Index of first record to return.
        max_results : int
            Max number of results to return.
        """

        _logger.debug('search() jql=%s, start_at=%d, max_results=%d',
                      jql, start_at, max_results)

        url = _SEARCH.format(*self.server, urllib.parse.quote_plus(jql),
                             start_at, max_results)

        try:
            _logger.debug('GET: %s', url)
            res = requests.get(url, auth=self.auth)

        except requests.exceptions.ConnectionError:
            _logger.error('Failed to connect to iTrack API server')
        else:
            code = res.status_code
            if code == 200:
                return res.json()
            elif code == 500:
                err = res.json()
                _logger.error('JQL search failed, error = %s', err, exc_info=1)
            else:
                _logger.error('JQL search failed, code = %d', code, exc_info=1)

        return {}
