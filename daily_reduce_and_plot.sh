#!/bin/bash
set -e
cd "$( dirname "${BASH_SOURCE[0]}" )"
./reduce_boulders.py data/scraping/ data/reduced/
./view_boulders.py data/reduced/latest_boulders.pkl data/plots/boulders.html
