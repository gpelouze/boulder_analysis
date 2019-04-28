#!/usr/bin/env python3

import datetime
import glob
import os
import pickle
import re
import warnings

from dateutil.parser import parse as parse_date
import numpy as np
import pandas as pd

import manage_data

def get_previous_reduced_file(output_dir):
    try:
        latest_reduced_file = os.readlink(
            os.path.join(output_dir, 'latest_boulders.pkl'))
        latest_reduced_file = os.path.join(output_dir, latest_reduced_file)
    except FileNotFoundError:
        existing_reduced_files = sorted(glob.glob(
            os.path.join(output_dir, '*.pkl')))
        if existing_reduced_files:
            latest_reduced_file = existing_reduced_files[-1]
        else:
            raise FileNotFoundError('no reduced data found')
    return latest_reduced_file


def list_files_to_reduce(input_dir, previous_boulders):
    input_files = sorted(glob.glob(os.path.join(input_dir, '*.yml')))

    if previous_boulders is None:
        return input_files

    latest_reduced_date = max([t.date.max() for t in previous_boulders.time])

    input_files = np.array(input_files)
    date_in_filename_re = re.compile('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}')
    input_files_dates = [parse_date(date_in_filename_re.findall(fn)[0])
                         for fn in input_files]
    input_files_dates = np.array(input_files_dates)
    input_files_to_reduce = input_files[input_files_dates > latest_reduced_date]
    return list(input_files_to_reduce)


class Output():
    def __init__(self, args):
        self.args = args
        self.timestamp = datetime.datetime.now().isoformat()
        self.write_mode # raise exception if output file exists

    @property
    def filename(self):
        os.makedirs(self.args.output_dir, exist_ok=True)
        return os.path.join(
            self.args.output_dir,
            'boulders_{}.pkl'.format(self.timestamp))

    @property
    def filename_latest(self):
        return os.path.join(self.args.output_dir, 'latest_boulders.pkl')

    @property
    def write_mode(self):
        if os.path.exists(self.filename):
            raise ValueError('output file exists')
        else:
            return 'wb'


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Reduce scraped boulder data.')
    parser.add_argument(
        'input_dir',
        type=str,
        help='directory containing scrape_boulder.py yaml outputs')
    parser.add_argument(
        'output_dir',
        type=str,
        help='directory where results are saved')
    args = parser.parse_args()

    output = Output(args)

    try:
        previous_boulders = pd.read_pickle(
            get_previous_reduced_file(args.output_dir))
    except FileNotFoundError:
        previous_boulders = None
        warnings.warn('found no previously reduced data')

    files_to_reduce = list_files_to_reduce(args.input_dir, previous_boulders)
    files_to_reduce = files_to_reduce
    new_boulders = manage_data.boulders_yaml_to_dataframe(files_to_reduce)

    boulders = manage_data.update_boulders(previous_boulders, new_boulders)

    with open(output.filename, output.write_mode) as f:
        pickle.dump(boulders, f)

    os.unlink(output.filename_latest)
    os.symlink(output.filename, output.filename_latest)
