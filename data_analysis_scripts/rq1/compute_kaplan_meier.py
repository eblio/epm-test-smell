'''
Kaplan Meier survival analysis on Github issues.
'''

import os
import json
import utils
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sksurv.nonparametric import kaplan_meier_estimator
from sksurv.functions import StepFunction
from sklearn.decomposition import PCA

ISSUES_PATH = '../../data/rq1/android_issues/'
OUT_FILE = '../../data/rq1/figures/km_curves.pdf'

def parse_args():
    '''
    Creates and parses command line arguments.
    '''
    parser = argparse.ArgumentParser(description='Compute Github project issues survival analysis.')
    parser.add_argument('-m', '--mode', dest='mode', help='Normalize files, compute or plot.')
    return parser.parse_args()


def normalize_issue_file(filename):
    '''
    Normalizes all files.
    '''
    path = ISSUES_PATH + filename
    data = {}

    with open(path, 'r') as f:
        prev_data = json.load(f)

        if isinstance(prev_data, dict):
            data = prev_data
        else:
            data['issues'] = prev_data

    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def normalize_issues_files():
    '''
    Normalizes the issues JSON objects.
    '''
    for filename in os.listdir(ISSUES_PATH):
        normalize_issue_file(filename)


def compute_issue_lifespan(issue):
    '''
    Computes the issue JSON object lifespan.
    '''
    event = True
    lifespan = 0

    # Do not compute already existing data
    if 'lifespan' in issue:
        event = issue['closed_at'] != 'None'
        lifespan = issue['lifespan']
    else:
        if issue['closed_at'] == 'None':
            event = False
            lifespan = abs((utils.string_to_date(issue['opened_at']) -
                        datetime.now()).days)
        else:
            lifespan = abs((utils.string_to_date(issue['opened_at']) -
                        utils.string_to_date(issue['closed_at'])).days)

        issue['lifespan'] = lifespan

    return event, lifespan


def compute_repo_issues_survival(filename):
    '''
    Computes a repository survival analysis of issues.
    '''

    # Load the repository data
    data = {}

    with open(ISSUES_PATH + filename, 'r') as f:
        data = json.load(f)

    # Compute the issues lifespan
    events = []
    lifespans = []

    for issue in data['issues']:
        event, lifespan = compute_issue_lifespan(issue)
        events.append(event)
        lifespans.append(lifespan)

    # Compute the survival analysis
    time, prob_survival = kaplan_meier_estimator(events, lifespans)
    data['time'] = time.tolist()
    data['prob_survival'] = prob_survival.tolist()

    # Save the results for later use
    with open(ISSUES_PATH + filename, 'w') as f:
        json.dump(data, f, indent=4)


def compute_all_repo_issues_survival():
    '''
    Computes all repositories survival analysis of issues.
    '''
    for filename in os.listdir(ISSUES_PATH):
        compute_repo_issues_survival(filename)


def draw_curves(repo_time, repo_prob, all_time, all_prob):
    '''
    Draws the survival curves.
    '''
    f, (a1, a2) = plt.subplots(ncols=2)

    a1.set_axisbelow(True)
    a1.grid()
    a1.set(xlabel='time [days]', ylabel='survival probability', ylim=(0, 1))
    a1.step(repo_time, repo_prob, where='post', color='#0F0F0F')
    a1.set_box_aspect(1)

    a2.set_axisbelow(True)
    a2.grid()
    a2.set(xlabel='time [days]', ylabel='survival probability', ylim=(0, 1))
    a2.step(all_time, all_prob, where='post', color='#0F0F0F')
    a2.set_box_aspect(1)

    plt.subplots_adjust(wspace=0.3)
    # plt.show()
    plt.savefig(OUT_FILE, format='pdf', bbox_inches='tight')
    

def plot_one_repo_and_all():
    '''
    Plot suvival curves for one significative repo and all others combined.
    '''

    # Get repo data
    repo = 'xbmc_xbmc.json'
    repo_data = {}

    with open(ISSUES_PATH + repo, 'r') as f:
        repo_data = json.load(f)

    repo_time = repo_data['time']
    repo_prob = repo_data['prob_survival']

    # Get all data
    events = []
    lifespans = []

    for filename in os.listdir(ISSUES_PATH):
        data = {}

        with open(ISSUES_PATH + filename, 'r') as f:
            data = json.load(f)

        for issue in data['issues']:
            events.append(issue['closed_at'] != 'None')
            lifespans.append(issue['lifespan'])

    all_time, all_prob = kaplan_meier_estimator(events, lifespans)

    # Plot everything
    draw_curves(repo_time, repo_prob, all_time, all_prob)


def get_survival_prob(issues):
    '''
    Gets the survival probabilities based on the issue object.
    '''
    f = StepFunction(np.array(issues['time']), np.array(issues['prob_survival']))
    prob = None

    try:
        prob = {
            '1 days': f(1),
            '2 days':f(2),
            '3 days': f(3),
            '7 days': f(7),
            '30 days': f(30),
            '100 days': f(100),
            '365 days': f(365)
        }
    except:
        pass # The dataset might not reach our necessary boundaries

    return prob


def main_component_analysis():
    '''
    Performs a main component analysis on the Kaplan Meier analysis.
    https://stackoverflow.com/questions/50796024/feature-variable-importance-after-a-pca-analysis
    '''

    prob_data = pd.DataFrame()

    # Collect the data for the PCA
    for filename in os.listdir(ISSUES_PATH):
        with open(ISSUES_PATH + filename, 'r') as f:
            data = json.load(f)
            name = utils.filename_to_name(filename)
            prob = get_survival_prob(data)

            if prob != None:
                prob_data = prob_data.append(prob, ignore_index=True)

    # Compute the components variance
    pca = PCA(n_components=7)
    pca.fit_transform(prob_data)

    print('Variance of each component : ' + str(pca.explained_variance_ratio_))

    most_important = [np.abs(pca.components_[i]).argmax() for i in range(7)]
    most_important_names = [prob_data.columns[most_important[i]] for i in range(7)]
    
    print('Importance of each : ' + str(most_important_names))


if __name__ == '__main__':
    args = parse_args()

    if args.mode == 'norm':
        normalize_issues_files()
    elif args.mode == 'comp':
        compute_all_repo_issues_survival()
    elif args.mode == 'plot':
        plot_one_repo_and_all()
    elif args.mode == 'main':
        main_component_analysis()
