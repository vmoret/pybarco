"""Provides iTrack reporting functions"""
import functools
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from pandas.tseries.offsets import BDay
import matplotlib.pyplot as plt
import seaborn as sns

from . import api
from ..utils.recipes import const, bool2int
from ..auth import BasicAuth

sns.set(style='white')
sns.set_palette(sns.color_palette("Paired"))

AUTH = BasicAuth.from_env('ITRACK')
SERVER = ('itrack.barco.com', 443)
TODAY = datetime.today().date()
LAST_YEAR = TODAY - timedelta(days=356)
BLUE, DARK_BLUE, GREEN, DARK_GREEN, RED, DARK_RED = sns.color_palette()
MARKERS = ['D', '*', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p',
           ',', 'h', 'H', '+', 'x', '.', 'd']


def add_metadata(data, config, pqm=True, experience=True):
    """
    Adds PQM and Experience metadata to `data`.

    Parameters
    ----------
    data -- pandas.DataFrame
    config -- dict
        Mapping with the PQM configuration
    pqm, experience -- bool
        Flags indicating whether or not to add the respective column
    """
    df = data.copy()
    if pqm:
        df['PQM'] = df.project.map(lambda x: config.get(x, 'Other'))
    if experience:
        df['Experience'] = df.project.map(
            lambda x: config.get(x, 'Other-').split('-')[0]
        )
    return df


def add_measures(data):
    """
    Adds the measures columns to `data`.

    Parameters
    ----------
    data -- pandas.DataFrame
    """

    def _busday(start, end, n=1):
        def _inner(df):
            return ((df[start].fillna(TODAY) + BDay(n) >= df[end].fillna(TODAY))
                    .map(bool2int))
        return _inner

    measures = ('N', 'FRT_10', 'TRT_20')
    funcs = (const(1), _busday('created', 'investigated', n=10),
             _busday('created', 'closuredate', n=20))

    df = data.copy().assign(
        **{k: func for k, func in zip(measures, funcs)}
    )

    # these measures make no sense for the recent dates --> clear these
    for measure, n in zip(measures[1:], (10, 20)):
        df.loc[df.created >= TODAY - BDay(n), measure] = np.nan

    return df


def calculate_trend(data, start=LAST_YEAR):
    """
    Calculates trend measures for `data`.

    Parameters
    ----------
    data -- pandas.DataFrame
    """
    def _timeseries(data, x='created', y='N', agg='sum', freq='B'):
        return (data.rename(columns={x:'DT'}).set_index('DT').sort_index()
                .resample(freq)[y].agg(agg).fillna(0))

    return pd.DataFrame(dict(
        created=_timeseries(data),
        resolved=_timeseries(data, x='closuredate'),
        FRT_10=_timeseries(data, y='FRT_10', agg='mean'),
        TRT_20=_timeseries(data, y='TRT_20', agg='mean')
    ))[start:]


def load(config, start=LAST_YEAR):
    """
    Returns the active and hist aspect of the iTrack report.

    Parameters
    ----------
    config -- dict
        Mapping with a 'pqms' key with the project to PQM mapping
    """

    # load the history
    JQL = 'filter=26769 and (created > {0:%Y-%m-%d} or closed > {0:%Y-%m-%d})'
    jql = JQL.format(start)
    hist = api.search(
        jql, auth=AUTH, server=SERVER
    ).pipe(add_metadata, config['pqms']).pipe(add_measures)

    # load the active
    active = api.search(
        'filter=27347', auth=AUTH, server=SERVER
    ).pipe(add_metadata, config['pqms'])

    return active, hist


def pyplot(title=None, xlabel=None, ylabel=None, legend=True):
    """
    Decorator factory adding formatting matplotlib Axes returned from decorated
    function.

    Parameters
    ----------
    title -- Unicode
        the title to add to the Axes
    xlabel -- Unicode
        the label of the X-axis of the Axes
    ylabel -- Unicode
        the label of the Y-axis of the Axes
    legend -- bool
        whether or not to show the legend
    """
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            ax = func(*args, **kwargs)
            if title is not None:
                ax.set_title(title, loc='left')
            if xlabel is not None:
                ax.set_xlabel(xlabel)
            if ylabel is not None:
                ax.set_ylabel(ylabel)
            if legend:
                ax.legend(loc='best', fancybox=True, framealpha=0.5)
            sns.despine(ax=ax)
            return ax
        return _wrapper
    return _decorator


@pyplot(
    title='Age vs. Idle (active)',
    xlabel='Age (BD)', ylabel='Idle (BD)'
)
def age_vs_idle_scatter(data, ax):
    """
    Plots Age vs. Idle of `data` on Axes `ax`.

    Parameters
    ----------
    data -- pandas.DataFrame
    ax -- matplotlib.axes.Axes
    """
    groups = data.groupby('status')
    kws = dict(alpha=0.9, ls='')
    for lbl, grp, m in zip(*zip(*groups), MARKERS):
        ax.plot(grp.age, grp.idle, label=lbl, marker=m, **kws)
    return ax


@pyplot(
    title='Priority vs. Severity (active)',
    ylabel='Tickets'
)
def priority_vs_severity_bars(data, ax):
    """
    Plots priority vs. severity of `data` on Axes `ax`.

    Parameters
    ----------
    data -- pandas.DataFrame
    ax -- matplotlib.axes.Axes
    """
    data.copy().assign(N=1).groupby(
        ['priority', 'severity']
    ).N.sum().unstack().plot.bar(stacked=True, ax=ax)
    return ax


@pyplot(
    title='Status (active)', legend=False
)
def status_pie(data, ax, n=4):
    """
    Plots status pie chart of `data` on Axes `ax`.

    Parameters
    ----------
    data -- pandas.DataFrame
    ax -- matplotlib.axes.Axes
    """
    ys = data.status.value_counts()
    selected = ys.nlargest(n)
    other = sum(v for k, v in ys.items() if k not in selected.index.tolist())
    items = list(selected.items()) + [('Other', other)] if other > 0 else list(selected.items())
    labels, sizes = zip(*items)
    ax.pie(sizes, labels=labels, autopct='%1.0f%%', shadow=True)
    return ax


@pyplot(
    title='PQM (active)', legend=False
)
def pqm_pie(data, ax, n=4):
    """
    Plots PQM pie chart of `data` on Axes `ax`.

    Parameters
    ----------
    data -- pandas.DataFrame
    ax -- matplotlib.axes.Axes
    """
    ys = data.PQM.value_counts()
    selected = ys.nlargest(n)
    other = sum(v for k, v in ys.items() if k not in selected.index.tolist())
    items = list(selected.items()) + [('Other', other)] if other > 0 else list(selected.items())
    labels, sizes = zip(*items)
    ax.pie(sizes, labels=labels, autopct='%1.0f%%', shadow=True)
    return ax


@pyplot(
    title='Created vs. Resolved (CUMUL)',
    ylabel='Tickets'
)
def created_vs_resolved_cumul(data, ax):
    """
    Plots created vs. resolved (cumulative) of `data` on Axes `ax`.

    Parameters
    ----------
    data -- pandas.DataFrame
    ax -- matplotlib.axes.Axes
    """
    columns = ('created', 'resolved')
    x = data.index
    ys = [data[col].cumsum() for col in columns]
    for y, lbl, color in zip(ys, ['Created', 'Resolved'], [RED, GREEN]):
        ax.plot(x, y, label=lbl, color=color)
    y1, y2 = ys
    ax.fill_between(x, y1, y2, where=y1 >= y2, facecolor=RED, alpha=0.1)
    ax.fill_between(x, y2, y1, where=y2 >= y1, facecolor=GREEN, alpha=0.1)
    return ax


@pyplot(
    title='Unresolved (CUMUL)',
    ylabel='Tickets'
)
def unresolved_cumul(data, ax):
    """
    Plots unresolved (cumulative) of `data` on Axes `ax`.

    Parameters
    ----------
    data -- pandas.DataFrame
    ax -- matplotlib.axes.Axes
    """
    x = data.index
    y = data.created.cumsum() - data.resolved.cumsum()
    ax.plot(x, y, label='$\Delta$ Unresolved', color=BLUE)
    return ax


@pyplot(
    title='Created vs. Resolved (7MA)',
    ylabel='Tickets'
)
def created_vs_resolved_rolling(data, ax):
    """
    Plots created vs. resolved (7MA) of `data` on Axes `ax`.

    Parameters
    ----------
    data -- pandas.DataFrame
    ax -- matplotlib.axes.Axes
    """
    columns = ('created', 'resolved')
    x = data.index
    ys = [data[col].rolling(7).mean() for col in columns]
    for y, lbl, color in zip(ys, ['Created', 'Resolved'], [RED, GREEN]):
        ax.plot(x, y, label=lbl, color=color)
    y1, y2 = ys
    ax.fill_between(x, y1, y2, where=y1 >= y2, facecolor=RED, alpha=0.1)
    ax.fill_between(x, y2, y1, where=y2 >= y1, facecolor=GREEN, alpha=0.1)
    return ax


@pyplot(
    title='Responsiveness (7MA)',
    ylabel='Percentage'
)
def responsiveness_rolling(data, ax):
    """
    Plots responsiveness (7MA) of `data` on Axes `ax`.

    Parameters
    ----------
    data -- pandas.DataFrame
    ax -- matplotlib.axes.Axes
    """
    columns = ('FRT_10', 'TRT_20', 'created')
    x = data.index
    y1, y2, total = [data[col].rolling(7).mean() for col in columns]
    y1.loc[TODAY - pd.tseries.offsets.BDay(10):] = np.nan
    y2.loc[TODAY - pd.tseries.offsets.BDay(20):] = np.nan
    ax.plot(x, y1 * 100 / total, label='% Investigated < 10BD', color=BLUE, ls='--')
    ax.plot(x, y2 * 100 / total, label='% Resolved < 20BD', color=BLUE)
    ax.set_ylim([0, 100])
    return ax


def plot(active, trend, options):

    fig = plt.figure(figsize=(11, 11))
    fig.suptitle(options['name'])

    grid_specs = [(0, 0, 3, 1), (1, 0, 3, 1), (2, 0, 3, 1), (3, 0, 3, 1),
                  (0, 3, 3, 1), (1, 3, 3, 1), (2, 3, 3, 1), (3, 3, 3, 1),]

    axes = [plt.subplot2grid((4, 5), (x, y), colspan=c, rowspan=r)
            for x, y, c, r in grid_specs]

    created_vs_resolved_cumul(trend, axes[0])
    unresolved_cumul(trend, axes[1])
    created_vs_resolved_rolling(trend, axes[2])
    responsiveness_rolling(trend, axes[3])
    age_vs_idle_scatter(active, axes[4])
    status_pie(active, axes[5])
    priority_vs_severity_bars(active, axes[6])
    pqm_pie(active, axes[7])

    plt.tight_layout()
    fig.subplots_adjust(bottom=0.1, top=0.9)

    created = int(trend.created.sum())
    resolved = int(trend.resolved.sum())
    high = len(active.query('severity == "S1" | priority == "P1"'))
    total = len(active)

    txt1 = r'Trend: {:d} created and {:d} resolved in last 356 days'.format(
        created, resolved
    )
    fig.text(0.5, 0.04, txt1, horizontalalignment='center')
    txt2 = r'Active: {:d} total and {:d} P1/S1'.format(total, high)
    fig.text(0.5, 0, txt2, horizontalalignment='center')

    return fig
