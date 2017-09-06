import re
from ...utils.decorators import with_default

ALL_CAPS_RE = re.compile(r'([A-Z]{2,} )')
ITRACK_REGEX = r'(\w{2,}\d{4,}-\d{1,})'
KB_REGEX = r'(KB.*\b)'


@with_default('Undefined')
def strpname(s):
    """Parses employee / contact name from `s`"""
    return ALL_CAPS_RE.sub('', str(s).split(' / ')[0])


@with_default('Unassigned')
def strpgroup(s):
    """Parses group name from `s`"""
    return str(s).split(' ')[0]


@with_default('Undefined')
def parse_itrack(df, column='Customer Reference', regex=ITRACK_REGEX):
    """
    Parses iTrack number from records in pandas DataFrame `df` `column`.

    Parameters
    ----------
    df -- pandas.DataFrame
    column -- str
    regex -- str
    """
    return df[column].str.extract(regex, expand=True)


@with_default('Undefined')
def parse_kb(df, column='Legacy Reference', regex=KB_REGEX):
    """
    Parses KB number from records in pandas DataFrame `df` `column``.

    Parameters
    ----------
    df -- pandas.DataFrame
    column -- str
    regex -- str
    """
    return df[column].str.extract(regex, expand=True)
