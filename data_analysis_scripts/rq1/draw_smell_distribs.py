'''
This file draw smells distribution for various groups.
'''

import utils
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

OUT_FORMAT = '../../data/rq1/figures/{}_vs_{}.pdf'
GROUPS_PATH = '../../data/rq1/groups/'
SMELLS_NAME = [
    'Assertion Roulette', 
    'Conditional Test Logic', 
    'Constructor Initialization', 
    'Default Test', 
    'EmptyTest', 
    'Exception Catching Throwing', 
    'General Fixture', 
    'Mystery Guest', 
    'Print Statement', 
    'Redundant Assertion', 
    'Sensitive Equality', 
    'Verbose Test', 
    'Sleepy Test', 
    'Eager Test',
    'Lazy Test', 
    'Duplicate Assert', 
    'Unknown Test', 
    'IgnoredTest', 
    'Resource Optimism', 
    'Magic Number Test', 
    'Dependent Test'
]

DEFAULT_DICT = {}
for n in SMELLS_NAME:
    DEFAULT_DICT[n] = 0

def column_to_sum(col):
    '''
    Converts a column indicating smell presence to an int.
    '''
    s = 0

    for v in col:
        if v:
            s += 1

    return s


def get_smell_distrib(names):
    '''
    Gets the smell distribution for a group if projects names.
    '''
    smell_distrib = DEFAULT_DICT.copy()
    total = 0

    # Compute occurences
    for n in names:
        filename = utils.project_name_to_file_name(utils.name_to_project_name(n))
        data = pd.read_csv(filename)

        # Iterate over the smells and compute the sum
        for name, occurences in data.items():
            if name in smell_distrib:
                occ = column_to_sum(occurences)
                smell_distrib[name] += occ
                total += occ
    
    # Convert to percentages
    for name, occurence in smell_distrib.items():
        smell_distrib[name] = occurence / total

    return smell_distrib


def draw_distrib(d1, d2, n1, n2):
    '''
    Draws two distributions with their name.
    '''
    y = np.arange(len(d1))
    barwidth = 0.3
    padding = barwidth / 5
    y1 = y - padding
    y2 = y + barwidth + padding

    plt.figure()

    plt.barh(y1, d1.values(),
             height=barwidth, color='#DFDFDF', edgecolor='#262626')
    plt.barh(y2, d2.values(),
             height=barwidth, color='#404040', edgecolor='#242424')

    plt.yticks(y + barwidth / 2, d1.keys())
    plt.legend(labels=[n1, n2])

    plt.show()
    # plt.savefig(OUT_FILE, format='pdf', bbox_inches='tight')


def main():
    '''
    Processes our groups files.
    '''
    all_projects = pd.read_csv('../../data/rq1/repos_stars.csv')
    bad_stars = pd.read_csv(GROUPS_PATH + 'bad_quality_stars.csv')
    good_stars = pd.read_csv(GROUPS_PATH + 'good_quality_stars.csv')
    bad_issues = pd.read_csv(GROUPS_PATH + 'bad_quality_issues.csv')
    good_issues = pd.read_csv(GROUPS_PATH + 'good_quality_issues.csv')

    draw_distrib(
        get_smell_distrib(bad_stars['name']),
        get_smell_distrib(good_stars['name']),
        'Low amount of stars',
        'High amount of stars'
    )

    draw_distrib(
        get_smell_distrib(bad_issues['name']),
        get_smell_distrib(good_issues['name']),
        'High issue survival',
        'Low issue survival'
    )


if __name__ == '__main__':
    main()
