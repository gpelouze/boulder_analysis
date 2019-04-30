#!/usr/bin/env python3

import datetime
import warnings

from dateutil.parser import parse as parse_date
import pandas as pd
import tqdm
import yaml

import models

def ejson_date_to_datetime(d):
    ''' Parse an ejson date, and return a datetime.datetime object '''
    return datetime.datetime.fromtimestamp(d['$date'] / 1e3)

def _get_all_prop_values(yaml_data, dates, b_id, prop, func=None):
    ''' Extract values at all sampled dates for a given property and boulder

    Roughly equivalent to returning:

        [func(yaml_data[d][b_id][prop]) for d in dates]

    but without raising an exception on boulders that are added or removed
    during the sampling period.

    Parameters
    ==========
    yaml_data : dict
        Data loaded from yaml files written by scrape_boulders.py.
    dates : list of str
        The sample dates, which are keys of yaml_data.
    b_id : str
        The id of the boulder from which to extract the property.
    prop : str
        The key of the property to extract.
    func : callable or None (default: None)
        If not None, apply this function to all elements before returning them.

    Returns
    =======
    values : list
    '''
    values = []
    for date in dates:
        boulder = yaml_data[date].get(b_id)
        if boulder:
            value = boulder.get(prop)
            if func is not None:
                try:
                    value = func(value)
                except:
                    value = None
            values.append(value)
    return values

def boulders_yaml_to_dataframe(yaml_files):
    ''' Convert yaml files from scrape_boulders.py to a single dataframe

    Parameters
    ==========
    yaml_files : list of str
        A list of yaml filenames written by scrape_boulders.py

    Returns
    =======
    boulders_df : pandas.DataFrame
        A dataframe containing all the boulders properties, including time
        resolved values of sentsCount, likesCount, and likesRatio.
    '''
    yaml_data = {}
    for fn in tqdm.tqdm(yaml_files, desc='Loading yaml data'):
        with open(fn) as f:
            f_data = yaml.load(f)
            for k, v in f_data.items():
                if k not in yaml_data:
                    yaml_data[k] = v
                else:
                    warnings.warn('ignoring duplicate date in yaml_data')

    # extract date and boulder_id keys
    boulders_id = set([k for d in yaml_data.values() for k in d.keys()])
    dates_str = sorted([d for d in yaml_data.keys()])
    dates_datetime = [parse_date(d) for d in dates_str]
    # add these keys to the boulder data
    for date_str, date_datetime in zip(dates_str, dates_datetime):
        for id_ in boulders_id:
            b = yaml_data[date_str].get(id_)
            if b:
                b['id'] = id_
                b['date'] = date_datetime

    boulder_props_use = {
        'attribute': (
            ('id', str),
            ('addedAt', ejson_date_to_datetime),
            ('boulderNum', int),
            ('closedAt', ejson_date_to_datetime),
            ('comment', str),
            ('createdAt', ejson_date_to_datetime),
            ('girly', bool),
            ('grade', int),
            ('gym', str),
            ('holdsColor', int),
            ('label', int),
            ('picture', models.Picture),
            ('routeSetter', list),
            ('routeTypes', list),
            ('updatedAt', ejson_date_to_datetime),
            ('zone', int),
            ),
        'derived_attributes': ( # properties derived from above processed attributes
            ('url', ('id', 'gym'), models.get_boulder_page_url),
            ),
        'time_series': (
            ('date', None),
            ('likesCount', None),
            ('likesRatio', None),
            ('sentsCount', None),
            ),
        'discard': (
            'dislikesList',
            'likesList',
            'projectsList',
            'sentsList',
            ),
        }

    boulders_df = pd.DataFrame()
    for b_id in boulders_id:
        boulder_props = {}
        for prop, func in boulder_props_use['attribute']:
            values = _get_all_prop_values(yaml_data, dates_str, b_id, prop)
            try:
                value = values[-1]
                if func:
                    value = func(value)
            except:
                value = None
            boulder_props[prop] = value
        for new_prop, src_props, func in boulder_props_use['derived_attributes']:
            src_props_values = [boulder_props[p] for p in src_props]
            value = func(*src_props_values)
            boulder_props[new_prop] = value
        time_data = {}
        for prop, func in boulder_props_use['time_series']:
            time_data[prop] = _get_all_prop_values(yaml_data, dates_str, b_id, prop, func=func)
        boulder_props['time'] = pd.DataFrame(time_data)
        boulders_df = boulders_df.append([boulder_props])
    boulders_df = boulders_df.set_index(boulders_df.id)
    return boulders_df

def update_boulders(boulders, new_boulders):
    for b_id, b in new_boulders.iterrows():
        if b_id not in boulders.index:
            boulders = boulders.append(b)
        else:
            old_b = boulders.loc[b_id]
            time = pd.concat([old_b.time, b.time])
            b.time = time
            boulders.loc[b_id] = b
    return boulders
