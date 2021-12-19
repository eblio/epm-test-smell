'''
Classify our repositories into two groups.
'''

import os
import json
import utils
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sksurv.functions import StepFunction

ISSUES_PATH = '../../data/rq1/android_issues/'
STARS_FILE = '../../data/rq1/repos_stars.csv'
OUT_FILE = '../../data/rq1/figures/km_distrib.pdf'
OUT_PATH = '../../data/rq1/groups/'
CSV_HEADER = 'name\n'
FILE_NAMES = [
    'bad_quality_stars.csv',
    'good_quality_stars.csv',
    'bad_quality_issues.csv',
    'good_quality_issues.csv'
]

def get_quantile_indices(a, q):
    '''
    Gets the indices contained in the specified quantile.
    '''
    qv = np.quantile(a, q)
    return {i for i in range(len(a)) if a[i] <= qv}


def get_q1_q3_indices(a):
    '''
    Gets the indices contained in the first and third quartile. 
    '''
    return get_quantile_indices(a, 0.25), set(range(len(a))).difference(get_quantile_indices(a, 0.75))


def get_stars_classes():
    '''
    Gets the classes based on the number of stars.
    '''
    stars = pd.read_csv(STARS_FILE)
    
    q1_indices, q3_indices = get_q1_q3_indices(stars['log_stars'])
    
    low_stars = stars['name'][q1_indices]
    high_stars = stars['name'][q3_indices]

    return low_stars, high_stars


def draw_distribs(days, year):
    '''
    Draws the distribution of both metrics.
    '''
    f, (a1, a2) = plt.subplots(ncols=2)

    a1.set_axisbelow(True)
    a1.grid()
    # a1.set_title('Histogram of the number of stars')
    a1.set(xlabel='prob. of 3 days surv.', ylabel='projects')
    a1.hist(days, color='#E03015')
    a1.set_box_aspect(1)

    a2.set_axisbelow(True)
    a2.grid()
    # a2.set_title('Histogram of the logarithm of the number stars')
    a2.set(xlabel='prob. of 365 days surv.', ylabel='projects')
    a2.hist(year, color='#E03015')
    a2.set_box_aspect(1)

    plt.subplots_adjust(wspace=0.3)
    # plt.show()
    plt.savefig(OUT_FILE, format='pdf', bbox_inches='tight')


def get_survival_prob(issues):
    '''
    Gets the survival probabilities based on the issue object.
    '''
    f = StepFunction(np.array(issues['time']), np.array(issues['prob_survival']))
    days = None
    year = None

    try:
        days = f(30)
        year = f(365)
    except:
        pass # The dataset might not reach our necessary boundaries

    return days, year


def get_issues_classes():
    '''
    Gets the classes based on issues survival.
    '''
    issues = {'name': [], 'days': [], 'year': []}

    # Process the file to gather survival probabilities
    for filename in os.listdir(ISSUES_PATH):
        with open(ISSUES_PATH + filename, 'r') as f:
            data = json.load(f)
            name = utils.filename_to_name(filename)
            days, year = get_survival_prob(data)

            if days != None and year != None:
                issues['name'].append(utils.filename_to_name(filename))
                issues['days'].append(days)
                issues['year'].append(year)

    draw_distribs(issues['days'], issues['year'])

    # Compute the classes
    q1_indices_d, q3_indices_d = get_q1_q3_indices(issues['days'])
    q1_indices_y, q3_indices_y = get_q1_q3_indices(issues['year'])
    
    issues['name'] = pd.Series(issues['name']) # Convert for easier indexing

    low_days = issues['name'][q1_indices_d]
    high_days = issues['name'][q3_indices_d]

    low_year = issues['name'][q1_indices_y]
    high_year = issues['name'][q3_indices_y]

    return low_days, high_days, low_year, high_year


def get_classes():
    '''
    Gets the two classes on which we are going to base our analysis.
    '''
    low_stars, high_stars = get_stars_classes()
    low_days, high_days, low_year, high_year = get_issues_classes()

    good_surv = set(high_days).intersection(set(high_year))
    bad_surv = set(low_days).intersection(set(low_year))

    print('{} projects with high quality issue survival'.format(len(good_surv)))
    print('{} projects with low quality issue survival'.format(len(bad_surv)))
    print('{} projects with high number of stars'.format(len(high_stars)))
    print('{} projects with low number of stars'.format(len(low_stars)))

    return low_stars, high_stars, bad_surv, good_surv # Important order


def output_classes():
    '''
    Ouputs the generated classes into .csv files.
    '''
    groups = get_classes()

    for i in range(len(groups)):
        file_content = CSV_HEADER
        
        for name in groups[i]:
            file_content += name + '\n'

        with open(OUT_PATH + FILE_NAMES[i], 'w') as f:
            f.write(file_content)


if __name__ == '__main__':
    output_classes()
