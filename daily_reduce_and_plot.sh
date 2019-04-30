#!/bin/bash
./reduce_boulders.py data/scraping/ data/reduced/
./view_boulders.py data/reduced/latest_boulders.pkl data/plots/boulders.html
