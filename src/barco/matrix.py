import datetime
from functools import reduce
from itertools import groupby
from operator import itemgetter

import pandas as pd
from IPython.display import display_html


def matrix_chart(value_counts, title, ranges=(3, 5, 10)):

    MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
              'Oct', 'Nov', 'Dec')

    def get_color(count):
        if count == 0:
            return '#eee'
        elif count < ranges[0]:
            return '#c6e48b'
        elif count < ranges[1]:
            return '#7bc96f'
        elif count < ranges[2]:
            return '#239a3b'
        else:
            return '#196127'


    def build_svg_day(weekday, date, month, count, x):
        fmt = ('<rect class="day" width="10" height="10" x="{x}" y="{y}" ' +
               'fill="{color}" data-count="{count}" data-date="{date}"></rect>')
        y = weekday * 12
        color = get_color(count)
        return fmt.format(x=x, y=y, color=color, count=count, date=date)


    def build_svg_week(week, days):
        svg = '<g transform="translate({x}, 0)">'.format(x=week * 13)
        x = 13 - week
        for day in days:

            svg += build_svg_day(*day, x)
        return svg + '</g>'


    def build_svg_month(x, month):
        return '<text x="{x}" y="{y}" class="month">{month}</text>'.format(
            x=x, y=-10, month=month)


    def build_svg(dates, width=674, height=104):

        def list_date_tuples(start, end, counter):
            today = datetime.date.today()

            def _init_date_tuple(date):
                return (date.weekday(), date, MONTHS[date.month - 1],
                        counter(date))

            return [_init_date_tuple(d)
                    for d in (today - datetime.timedelta(days=start + x)
                    for x in reversed(range(end)))]

        def build_counter(xs, ys):
            def _inner(x):
                t = pd.Timestamp(x)
                return ys[xs.index(t)] if t in xs else 0
            return _inner

        # build the counter from `dates` -- this allows us to count how many
        # tickets are linked to a given `date`
        counter = build_counter(*list(zip(*dates)))

        # build a weeekday, date, month tuple list
        days = list_date_tuples(0, 365, counter)

        # ensure we start with a 1st day of the week -- a.k.a. Monday
        days = list_date_tuples(365, days[0][0], counter) + days

        def split(acc, curr):
            xs, i = acc
            if curr[0] == 0:
                return xs + [[curr]], i + 1
            xs[i] = xs[i] + [curr]
            return xs, i

        weeks = list(reduce(split, days, ([[]], 0))[0])

        def reducer(y, x):
            if len(y):
                prev = y[-1]
                if prev[1] == x[1]:
                    return y + [(prev[0] + 1, x[1])]
            return y + [x]

        months = [max(x[1]) for x in groupby(reduce(reducer, [(1, x[2])
                  for x in days if x[0] == 0], []), itemgetter(1))]

        svg = ('<svg width="{width}" height="{height}" ' +
               'class="js-calendar-graph-svg">').format(width=width,
                                                        height=height)
        svg += '<g transform="translate(16, 20)">'
        for i, week in enumerate(weeks):
            svg += build_svg_week(i, week)
        x = 12 + (months[0][0] * 12 if months[0][0] < 3 else 0)
        for i, month in enumerate(months):
            n, name = month
            if n > 2:
                svg += build_svg_month(x, name)
                x += n * 12

        svg += '''
        <text text-anchor="start" class="wday" dx="-14" dy="8"
            style="display: none;">Mon</text>
        <text text-anchor="start" class="wday" dx="-14" dy="20">Tue</text>
        <text text-anchor="start" class="wday" dx="-14" dy="32"
            style="display: none;">Wed</text>
        <text text-anchor="start" class="wday" dx="-14" dy="44">Thu</text>
        <text text-anchor="start" class="wday" dx="-14" dy="57"
            style="display: none;">Fri</text>
        <text text-anchor="start" class="wday" dx="-14" dy="69">Sat</text>
        <text text-anchor="start" class="wday" dx="-14" dy="81"
            style="display: none;">Sun</text>'''
        svg += '</g>'
        svg += '</svg>'
        return svg

    style = '''
    <style>
    .contrib-legend {
        float: right;
    }
    .contrib-legend .legend {
        position: relative;
        bottom: -1px;
        display: inline-block;
        margin: 0 5px;
        list-style: none;
    }
    .text-gray {
        color: #586069 !important;
    }
    .float-left {
        float: left !important;
    }
    .contrib-legend .legend li {
        display: inline-block;
        width: 10px;
        height: 10px;
    }
    .contrib-footer {
        padding: 0 10px 12px;
        font-size: 11px;
        padding-right: 16px !important;
        padding-left: 16px !important;
        padding-bottom: 4px !important;
        margin-right: 16px !important;
        margin-left: 16px !important;
        margin-top: 4px !important;
    }
    .border {
        border: 1px #d1d5da solid !important;
        border-radius: 3px !important;
        margin-bottom: 0px !important;
        padding-top: 8px !important;
        padding-bottom: 16px !important;
        line-height: 11px;
    }
    .calendar-graph {
        padding: 5px 0 0;
        text-align: center;
        height: 100% !important;
        width: 900px;
    }
    svg:not(:root) {
        overflow: hidden;
    }
    rect {
        shape-rendering: crispedges;
    }
    .calendar-graph text.month {
        font-size: 10px;
        fill: #767676;
    }
    .calendar-graph text.wday {
        font-size: 9px;
        fill: #767676;
    }
    </style>'''
    html = '''
    <div class="border">
        <div class="calendar-graph">{svg}</div>
        <div class="contrib-footer">
            <div class="float-left text-gray">{title}</div>
            <div class="contrib-legend text-gray"
                 title="A summary of service tickets opened in last 356 days.">
                Less
                <ul class="legend">
                    <li style="background-color: #eee"></li>
                    <li style="background-color: #c6e48b"></li>
                    <li style="background-color: #7bc96f"></li>
                    <li style="background-color: #239a3b"></li>
                    <li style="background-color: #196127"></li>
                </ul>
                More
            </div>
        </div>
    </div>'''
    return display_html(
        style + html.format(title=title, svg=build_svg(value_counts.items())),
        raw=True)
