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

    def get_thumbnail(pic):
        try:
            return pic.zoom
        except AttributeError:
            pass

    data = [
        # data source (in boulder), data name, process function
        ('gym',  None, None),
        ('id',  None, None),
        ('picture',  'thumbnail', get_thumbnail),
        ('zone',  None, None),
        ('holdsColor',  None, lambda c: PlotData.holds_colors[c]),
        ('grade',  None, lambda g: '{}'.format(g)),
        ('routeTypes',  None, None),
        ('routeSetter',  None, None),
        ('createdAt',  None, pd.to_datetime),
        ('addedAt',  None, pd.to_datetime),
        ('updatedAt', None, pd.to_datetime),
        ('closedAt', None, pd.to_datetime),
        ('url', None, None),
        ('comment', None, None),
        ]

    tooltips = [
        ('Pic', '<img src="@thumbnail" width="100" height="100"></img>'),
        ('Zone', '@zone'),
        ('Grade', '$color[swatch]:holdsColor'),
        ('Subgrade', '@grade'),
        ('Route types', '@routeTypes'),
        ('Routesetters', '@routeSetter'),
        ('Created at', '@createdAt{%F}'),
        # ('Added at', '@addedAt{%F}'),
        # ('Updated at', '@updatedAt{%F}'),
        ('Closed at', '@closedAt{%F}'),
        ]

    formatters = {
        'createdAt': 'datetime',
        'addedAt': 'datetime',
        'updatedAt': 'datetime',
        'closedAt': 'datetime',
        }

    time_series = [
        ('date', None),
        ('boulderAge', None),
        ('likesCount', None),
        ('likesRatio', None),
        ('sentsCount', None),
        ]

def get_boulder_data_source(boulder):
    n = len(boulder.time.index)
    boulder_data = boulder._asdict()
    source_data = {}
    plot_data = PlotData()
    for key_src, key_dst, func in plot_data.data:
        data = boulder_data[key_src]
        if func:
            data = func(data)
        if key_dst is None:
            key_dst = key_src
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
            line_color=plot_data.holds_colors[boulder.holdsColor],
            source=get_boulder_data_source(boulder),
            )

    bk.plotting.save(p)
