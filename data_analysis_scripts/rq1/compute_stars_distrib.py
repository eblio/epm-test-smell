'''
Computes the stars distributions. 
'''

import utils
import argparse
import pandas as pd
import matplotlib.pyplot as plt

OUT_FILE = '../../data/rq1/figures/stars_distrib.pdf'

def parse_args():
    '''
    Creates and parses command line arguments.
    '''
    parser = argparse.ArgumentParser(description='Computes the stars distributions.')
    parser.add_argument('-f', '--file', dest='file', help='File containing the repos data.')
    return parser.parse_args()


def load_data(file):
    '''
    Loads the data.
    '''
    data = pd.read_csv(file)
    return data['stars'], data['log_stars']


def draw_distribs(stars, log_stars):
    '''
    Draws the distribution of both metrics.
    '''
    f, (a1, a2) = plt.subplots(ncols=2)
    
    a1.set_axisbelow(True)
    a1.grid()
    # a1.set_title('Histogram of the number of stars')
    a1.set(xlabel='$stars$', ylabel='$projects$')
    a1.hist(stars, color='#E03015', log=True)
    a1.set_box_aspect(1)

    a2.set_axisbelow(True)
    a2.grid()
    # a2.set_title('Histogram of the logarithm of the number stars')
    a2.set(xlabel='$log_{10}(1 + stars)$', ylabel='$projects$')
    a2.hist(log_stars, color='#E03015')
    a2.set_box_aspect(1)

    plt.subplots_adjust(wspace=0.3)
    # plt.show()
    plt.savefig(OUT_FILE, format='pdf', bbox_inches='tight')


def load_and_draw(file):
    '''
    Executes the full pipeline.
    '''
    stars, log_stars = load_data(file)
    draw_distribs(stars, log_stars)


if __name__ == '__main__':
    args = parse_args()
    load_and_draw(args.file)
