#!/usr/bin/env python3

import datetime
import os
import multiprocessing as mp
import time

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
        self.timestamp = datetime.datetime.now().isoformat()

    @property
    def filename(self):
        if self.args.output is not None:
            filename = self.args.output
        else:
            filename = os.path.join(
                self.args.output_dir,
                self.args.gym.replace('/', '+'))
            os.makedirs(self.args.output_dir, exist_ok=True)
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

def worker(args):
    client = BouldersClient(args.url, args.gym)
    client.run_forever()
    data = client.collections['boulders']

    output = Output(args)
    with open(output.filename, output.write_mode) as f:
        yaml.dump({output.timestamp: data}, f,
                  default_flow_style=False, allow_unicode=True)
    print('Output written to:', output.filename)

def scrape_boulders(args):
    p = mp.Process(target=worker, args=(args,))
    try:
        p.start()
        p.join(args.timeout)
        if p.is_alive():
            p.terminate()
            if args.exit_on_timeout:
                raise TimeoutError('client reached timeout')
            else:
                print('client reached timeout')
    finally:
        p.terminate()

def scrape_boulders_loop(args):
    while True:
        start_time = time.time()
        scrape_boulders(args)
        elapsed = time.time() - start_time
        remaining = args.repeat - elapsed
        time.sleep(remaining)


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
        '--output-dir',
        type=str,
        default='.',
        help='directory where results are saved if --output is not specified')
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='overwrite the output file if it exists')
    parser.add_argument(
        '--append', '-a',
        action='store_true',
        help='append to the output file if it exists')
    parser.add_argument(
        '--timeout',
        type=int,
        help='scraping timeout in seconds')
    parser.add_argument(
        '--repeat',
        type=int,
        help='repeat scraping every n seconds until killed')
    parser.add_argument(
        '--no-exit-on-timeout',
        dest='exit_on_timeout',
        action='store_false',
        help=("don't exit on timeout (but still terminate current scraping); "
              "useful for with --repeat"))
    args = parser.parse_args()

    print('Scraping:', args.url, args.gym)
    if args.repeat:
        scrape_boulders_loop(args)
    else:
        scrape_boulders(args)
