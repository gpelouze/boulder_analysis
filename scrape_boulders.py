#!/usr/bin/env python3

import datetime
import os
import sys

import yaml
from PyQt5.QtCore import QUrl, QObject, QSize, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QApplication

class CustomProfile(QWebEngineProfile):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from fake_useragent import UserAgent
            ua = UserAgent()
            user_agent = ua.chrome
            self.setHttpUserAgent(user_agent)
        except ImportError:
            pass


class Communicator(QObject):
    def __init__(self, app, verbose=False):
        self.app = app
        self.verbose = verbose
        self.messages = []
        super().__init__()

    def _receive(self, msg):
        if self.verbose:
            print('--- Received:', msg)
        self.messages.append(msg)

    @pyqtSlot()
    def quitApp(self):
        if self.verbose:
            print('--- Received exit signal from js API')
        self.app.quit()

class LogCommunicator(Communicator):
    @pyqtSlot(str)
    def receive(self, msg):
        return self._receive(msg)

class DataCommunicator(Communicator):
    @pyqtSlot(list)
    def receive(self, msg):
        return self._receive(msg)

    def clean(self):
        clean_data = []
        for boulder in self.messages:
            clean_data.append({k: v for k, v in boulder})
        return clean_data


class Scraper(QWebEngineView):
    def __init__(self, url):
        self.html = None
        self.app = QApplication([])
        super().__init__()
        profile = CustomProfile('storage', self)
        webpage = QWebEnginePage(profile, self)
        self.setPage(webpage)
        self.loadFinished.connect(self._loadFinished)
        self.load(QUrl(url))
        self.show()
        self.app.exec_()

    def _loadFinished(self, result):
        self.channel = QWebChannel(self.page())
        self.page().setWebChannel(self.channel)
        self.log_comm = LogCommunicator(self.app, verbose=True)
        self.data_comm = DataCommunicator(self.app)
        self.channel.registerObject('log_comm', self.log_comm);
        self.channel.registerObject('data_comm', self.data_comm);

        with open('scraper.js') as f:
            js_scraper = f.read()
        self.page().runJavaScript(js_scraper, print)


def determine_output_file(args, timestamp=None):
    if args.output is not None:
        return args.output
    else:
        output = args.url
        output = output.split('https://')[1].replace('/', '+')
        if timestamp:
            output += '_{}.yml'.format(timestamp)
        else:
            output += '.yml'
        return output

def determine_write_mode(args):
    if os.path.exists(args.output):
        if args.overwrite and args.append:
            raise ValueError("received both --overwrite or --append")
        if args.overwrite:
            return 'w'
        elif args.append:
            return 'a'
        else:
            raise ValueError("output file exists")
    else:
        return 'w'


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        description='Scrape boulders page.')
    parser.add_argument(
        'url',
        type=str,
        help='address of the page to scrape')
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

    timestamp = datetime.datetime.now().isoformat(timespec='seconds') 
    if args.append:
        args.output = determine_output_file(args)
    else:
        args.output = determine_output_file(args, timestamp=timestamp)

    print('Scraping:', args.url)
    s = Scraper(args.url)

    mode = determine_write_mode(args)
    with open(args.output, mode) as f:
        data = s.data_comm.clean()
        yaml.dump({timestamp: data}, f,
                  default_flow_style=False, allow_unicode=True)
    print('Output written to:', args.output)
