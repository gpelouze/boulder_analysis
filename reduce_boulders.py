#!/usr/bin/env python3

import datetime
import os
import pickle

import manage_data

class Output():
    def __init__(self, args):
        self.args = args
        self.timestamp = datetime.datetime.now().isoformat()
        self.write_mode # raise exception if output file exists

    @property
    def filename(self):
        if self.args.output is not None:
            return self.args.output
        else:
            os.makedirs(self.args.output_dir, exist_ok=True)
            return os.path.join(
                self.args.output_dir,
                'boulders_{}.pkl'.format(self.timestamp))

    @property
    def write_mode(self):
        if os.path.exists(self.filename) and not self.args.overwrite:
            raise ValueError('output file exists')
        else:
            return 'wb'


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Reduce scraped boulder data.')
    parser.add_argument(
        'url',
        type=str,
        help='websocket url')
    parser.add_argument(
        'input',
        type=str,
        nargs='+',
        help='scraping yaml output')
    parser.add_argument(
        '--output',
        type=str,
        help='file where the reduced data are pickled and saved')
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='directory where results are saved if --output is not specified')
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='overwrite the output file if it exists')
    args = parser.parse_args()

    output = Output(args)

    boulders = manage_data.boulders_yaml_to_dataframe(args.input)
    with open(output.filename, output.write_mode) as f:
        pickle.dump(boulders, f)
