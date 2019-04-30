#!/usr/bin/env python3

import datetime

import bokeh as bk
import bokeh.plotting
import pandas as pd

class PlotData:
    holds_colors = {
        2: '#FFEB3B',
        3: '#008000',
        4: '#1E88E5',
        5: '#DD0000',
        6: '#000000',
        7: '#8A2BE2',
        }

    grades_linewidths = {
        1: .5,
        2: 1,
        3: 2,
        }

    tooltip_attributes = (
        # ('gym',  'gym', '@gym', 'printf', None),
        # ('id',  'id', '@id', 'printf', None),
        ('picture',  'pic', '<img src="@pic" width="100" height="100"></img>', 'printf', lambda p: p.zoom),
        ('zone',  'zone', '@zone', 'printf', None),
        ('holdsColor',  'grade', '$color[swatch]:grade', 'printf', lambda c: PlotData.holds_colors[c]),
        ('grade',  'subGrade', '@subGrade', 'printf', lambda g: '{}/3'.format(g)),
        # ('girly',  'girly', '@girly', 'printf', None), % always True
        ('routeTypes',  'routeTypes', '@routeTypes', 'printf', None),
        ('routeSetter',  'routeSetter', '@routeSetter', 'printf', None),
        ('createdAt',  'createdAt', '@createdAt{%F}', 'datetime', pd.to_datetime),
        ('addedAt',  'addedAt', '@addedAt{%F}', 'datetime', pd.to_datetime),
        ('updatedAt',  'updatedAt', '@updatedAt{%F}', 'datetime', pd.to_datetime),
        ('closedAt',  'closedAt', '@closedAt{%F}', 'datetime', pd.to_datetime),
        ('url', 'url', '@url', 'printf', None),
        # ('comment',  'comment', '@comment', 'printf', None), % there are never comments
        )

    time_series = (
        ('date', None),
        ('boulderAge', None),
        ('likesCount', None),
        ('likesRatio', None),
        ('sentsCount', None),
        )

    @property
    def tooltip_data(self):
        return [(ta[0], ta[1], ta[4]) for ta in self.tooltip_attributes]

    @property
    def tooltips(self):
        return [(ta[1], ta[2]) for ta in self.tooltip_attributes]

    @property
    def formatters(self):
        return {ta[1]: ta[3] for ta in self.tooltip_attributes}

def get_boulder_data_source(boulder):
    n = len(boulder.time.index)
    boulder_data = boulder._asdict()
    source_data = {}
    plot_data = PlotData()
    for key_src, key_dst, func in plot_data.tooltip_data:
        data = boulder_data[key_src]
        if func:
            data = func(data)
        source_data[key_dst] = [data]*n
    for key, func in plot_data.time_series:
        data = boulder.time[key]
        if func:
            data = [func(d) for d in data]
        source_data[key] = data
    source = bk.models.ColumnDataSource(data=source_data)
    return source


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Create bokeh view of boulders sents')
    parser.add_argument(
        'input_pkl',
        type=str,
        help='pkl file containing the reduced boulders dataframe')
    parser.add_argument(
        'output_html',
        type=str,
        help='output plot html file')
    args = parser.parse_args()

    boulders = pd.read_pickle(args.input_pkl)
    for boulder in boulders.itertuples():
        boulder_age = (boulder.time.date - boulder.addedAt).dt.total_seconds()
        boulder_age /= 86400 # seconds to days
        boulder.time['boulderAge'] = boulder_age


    plot_data = PlotData()
    hover_tool = bk.models.HoverTool(
        tooltips=plot_data.tooltips,
        formatters=plot_data.formatters,
        )
    tap_tool = bk.models.TapTool(
        callback=bk.models.OpenURL(url='@url'),
        )

    bk.plotting.output_file(args.output_html)
    p = bk.plotting.figure(
        title=list(set(boulders.gym))[0],
        x_axis_label='Problem age [days]',
        y_axis_label='Number of sents',
        tools='pan,box_zoom,wheel_zoom,save,reset',
        plot_height=800,
        plot_width=1000,
        )
    p.add_tools(hover_tool)
    p.add_tools(tap_tool)

    plot_boulders = boulders[boulders.closedAt > datetime.datetime.now()]
    for boulder in plot_boulders.itertuples():
        p.line(
            'boulderAge',
            'sentsCount',
            line_width=plot_data.grades_linewidths[boulder.grade],
            line_color=plot_data.holds_colors[boulder.holdsColor],
            source=get_boulder_data_source(boulder),
            )

    bk.plotting.save(p)
