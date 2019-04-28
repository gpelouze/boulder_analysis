#!/usr/bin/env python3

import glob
import os
import pickle

import matplotlib as mpl
import matplotlib.pyplot as plt

import manage_data

if __name__ == '__main__':

    boulders_path = 'data/reduced/latest_boulders.pkl'
    with open(boulders_path, 'rb') as f:
        boulders = pickle.load(f)

    colors = {
        2: '#FFEB3B',
        3: '#008000',
        4: '#1E88E5',
        5: '#DD0000',
        6: '#000000',
        7: '#8A2BE2',
        }
    linewidths = {
        1: .5,
        2: 1,
        3: 2,
        }

    plt.clf()
    for boulder in boulders.itertuples():
        boulder_age = (boulder.time.date - boulder.addedAt).dt.total_seconds()
        boulder_age /= 86400 # seconds to days
        plt.plot(
            boulder_age,
            boulder.time.sentsCount,
            '-',
            color=colors[boulder.holdsColor],
            linewidth=linewidths[boulder.grade],
            )
    plt.title(list(set(boulders.gym))[0])
    plt.xlabel('Problem age [days]')
    plt.ylabel('Number of sents')
    plt.savefig('data/plots/boulders.pdf')
