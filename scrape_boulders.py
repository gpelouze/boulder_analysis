#!/usr/bin/env python3

import datetime
import os

import yaml

from ddp_client import DDPClient

VERBOSE = False

class BouldersClient(DDPClient):
    def __init__(self, url, gym):
        super().__init__(url)
        self.gym = gym
        self.waiting_subs = set()

    def on_ready(self, subs):
        for sub in subs:
            self.waiting_subs.remove(sub)
        if not self.waiting_subs:
            self.close()

    def on_open(self):
        super().on_open()

        id_ = self.sub(
            '_boulders.list', [{'gym': self.gym, 'isClosed': None}, {}, 10000])
        self.waiting_subs.add(id_)

    def on_message(self, msg):
        msg = super().on_message(msg)
        if VERBOSE:
            print(msg)

class Output():
    def __init__(self, args):
        self.args = args
        self.timestamp = datetime.datetime.now().isoformat(timespec='seconds')

    @property
    def filename(self):
        if self.args.output is not None:
            filename = self.args.output
        else:
            filename = self.args.gym.replace('/', '+')
            if self.args.append:
                filename += '.yml'
            else:
                filename += '_{}.yml'.format(self.timestamp)
        return filename

    @property
    def write_mode(self):
        if os.path.exists(self.filename):
            if self.args.overwrite and self.args.append:
                raise ValueError('received both --overwrite or --append')
            if self.args.overwrite:
                return 'w'
            elif self.args.append:
                return 'a'
            else:
                raise ValueError('output file exists')
        else:
            return 'w'

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Scrape boulders data.')
    parser.add_argument(
        'url',
        type=str,
        help='websocket url')
    parser.add_argument(
        'gym',
        type=str,
        help='gym name')
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='yaml file where the results are saved')
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='overwrite the output file if it exists')
    parser.add_argument(
        '--append', '-a',
        action='store_true',
        help='append to the output file if it exists')
    args = parser.parse_args()
    output = Output(args)

    print('Scraping:', args.url, args.gym)
    client = BouldersClient(args.url, args.gym)
    client.run_forever()
    data = client.collections['boulders']

    with open(output.filename, output.write_mode) as f:
        yaml.dump({output.timestamp: data}, f,
                  default_flow_style=False, allow_unicode=True)
    print('Output written to:', output.filename)
