"""Provides functions to parse data objects returned from iTrack REST API."""
from datetime import datetime as dt
from functools import partial, reduce
import json

from pkg_resources import resource_stream
import numpy as np

from ..utils.recipes import compose, ident, itemgetter, splitstr, fst
from ..utils.decorators import join_with, strptime_with

# Load configuration file
_CONFIG = json.load(resource_stream(__name__, 'config.json'))

_CLOSED_STATES = _CONFIG['closed_states']
_DEFECT_TYPES = _CONFIG['issue_type']['defect']
_CHANGE_TYPES = _CONFIG['issue_type']['change']

# Initialize item getters
_get_name = itemgetter('name')
_get_value = itemgetter('value')
_get_archived = itemgetter('archived')


@join_with(',')
def _get_versions(sequence):
    def _reducer(acc, curr):
        return acc if _get_archived(curr) else acc + [_get_name(curr)]
    return reduce(_reducer, sequence, []) if isinstance(sequence, list) else []


@strptime_with()
def _get_date(s):
    return s.split('T')[0] if isinstance(s, str) else None


def _busday(obj, start, end=None, today=dt.today().date()):
    date = obj.get(end, today) if end in obj else today
    return np.busday_count(obj[start], date if date else today)

# field value converters
CONVERTERS = dict(
    assignee=compose(_get_name, str.upper),
    summary=ident,
    status=compose(_get_name, str.lower),
    issuetype=compose(_get_name, str.lower),
    project=_get_name,
    priority=compose(_get_name, splitstr, fst),
    customfield_10002=compose(_get_value, splitstr, fst),
    customfield_10021=_get_value,
    customfield_10232=_get_date,
    customfield_10350=_get_date,
    fixVersions=_get_versions,
    versions=_get_versions,
    created=_get_date,
    resolutiondate=_get_date,
    updated=_get_date,
    reported=compose(_get_name, str.upper)
)


def parse_itrack_issue(issue):
    """Parses iTrack issue mapping."""

    # get 'fields' from `issue`
    fields = issue.get('fields', {})

    # apply converters
    data = {k: f(fields[k]) for k, f in CONVERTERS.items() if k in fields}

    # add key
    data['key'] = issue.get('key', None)

    # add metadata
    data['closed'] = data.get('status', None) in _CLOSED_STATES
    data['defect'] = data.get('issuetype', None) in _DEFECT_TYPES
    data['change'] = data.get('issuetype', None) in _CHANGE_TYPES
    data['age'] = _busday(data, 'created', 'customfield_10350')
    data['idle'] = _busday(data, 'updated')

    return data
