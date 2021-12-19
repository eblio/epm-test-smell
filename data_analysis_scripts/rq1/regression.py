'''
Regression analysis of our data.
Number of stars % taille de la suite de test
Taille du projet % taille de la suite de test
Number of stars % nombre de tests smells + taille du projet
Pareil avec la probabilité de survie des issues ?
'''

import json
import utils
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress, spearmanr
from sksurv.functions import StepFunction

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

def plot(x, y, names=None):
    '''
    Plot the given data.
    '''
    f, ax = plt.subplots()

    ax.scatter(x, y)

    if not names is None:
        for i, n in enumerate(names):
            ax.annotate(n, (x[i], y[i]))

    plt.show()


def get_survival_prob(issues):
    '''
    Gets the survival probabilities based on the issue object.
    '''
    f = StepFunction(np.array(issues['time']),
                     np.array(issues['prob_survival']))
    days = None
    year = None

    try:
        days = f(30)
        year = f(365)
    except:
        pass  # The dataset might not reach our necessary boundaries

    return days, year


def column_to_sum(col):
    '''
    Converts a column indicating smell presence to an int.
    '''
    s = 0

    for v in col:
        if v:
            s += 1

    return s

def count_smells(smells):
    '''
    Gets the survival probabilities based on the issue object.
    '''
    s = 0

    for name, occurences in smells.items():
        if name in SMELLS_NAME:
            s += column_to_sum(occurences)
            
    return s


def java_smells_reg():
    '''
    Performs a regression analysis between the number of java files and the number test smells.
    '''
    java_file = pd.read_csv('../../data/rq1/repos_java_files.csv')
    smells = []

    for n in java_file['name']:
        data = pd.read_csv(utils.project_name_to_file_name(utils.name_to_project_name(n)))
        smells.append(count_smells(data))

    # plot(java_file['java_files'], smells)
    r = linregress(java_file['java_files'], smells)
    print('Linear regression : number of Java files % number of test smells : R²={} and p={}'.format(r.rvalue, r.pvalue))

def java_suite_reg():
    '''
    Performs a regression analysis between the number of java files and the number test files.
    '''
    input_file = pd.read_csv('../../data/rq1/repos_java_files.csv')

    # plot(input_file['java_files'], input_file['test_files'], names=input_file['name'])

    r = linregress(input_file['java_files'], input_file['test_files'])
    print('Linear regression : number of Java files % number of test files : R²={} and p={}'.format(r.rvalue, r.pvalue))


def stars_suite_reg():
    '''
    Performs a regression analysis between the number of stars and the number test files.
    '''
    stars_file = pd.read_csv('../../data/rq1/repos_stars.csv')
    suite_file = pd.read_csv('../../data/rq1/repos_java_files.csv')

    # plot(stars_file['log_stars'], suite_file['test_files'])

    r = linregress(stars_file['log_stars'], suite_file['test_files'])
    print('Linear regression : stars quality % number of test files : R²={} and p={}'.format(r.rvalue, r.pvalue))


def stars_smells_reg():
    '''
    Performs a regression analysis between the number of stars and the number test smells.
    '''
    stars_file = pd.read_csv('../../data/rq1/repos_stars.csv')
    smells = []

    smells = []

    for n in stars_file['name']:
        data = pd.read_csv(utils.project_name_to_file_name(utils.name_to_project_name(n)))
        smells.append(count_smells(data))

    # plot(stars_file['log_stars'], smells)
    r = linregress(stars_file['log_stars'], smells)
    print('Linear regression : stars quality % number of test smells : R²={} and p={}'.format(r.rvalue, r.pvalue))

def issues_suite_reg():
    '''
    Performs a regression analysis between the number of stars and the number test files.
    '''
    suite_file = pd.read_csv('../../data/rq1/repos_java_files.csv')
    surv = []
    suite = []

    for i, n in enumerate(suite_file['name']):
        with open('../../data/rq1/android_issues/' + utils.name_to_filename(n), 'r') as f:
            data = json.load(f)
            days, year = get_survival_prob(data)

            if days != None and year != None:
                suite.append(suite_file['test_files'][i])
                surv.append(year)

    # plot(surv, suite)

    r = linregress(surv, suite)
    # r2, p = spearmanr(surv, suite)
    print('Linear regression : issues quality % number of test files : R²={} and p={}'.format(r.rvalue, r.pvalue))
    # print('Spearman regression : issues quality % number of test files : R²={} and p={}'.format(r2, p))


def issues_smells_reg():
    '''
    Performs a regression analysis between the number of stars and the number test smells.
    '''
    suite_file = pd.read_csv('../../data/rq1/repos_java_files.csv')
    surv = []
    smells = []

    for i, n in enumerate(suite_file['name']):
        with open('../../data/rq1/android_issues/' + utils.name_to_filename(n), 'r') as f:
            data = json.load(f)
            days, year = get_survival_prob(data)

            if days != None and year != None:
                surv.append(days)

                data = pd.read_csv(utils.project_name_to_file_name(utils.name_to_project_name(n)))
                smells.append(count_smells(data))

    # plot(surv, smells)

    r = linregress(surv, smells)
    # r2, p = spearmanr(surv, suite)
    print('Linear regression : issues quality % number of test smells : R²={} and p={}'.format(r.rvalue, r.pvalue))
    # print('Spearman regression : issues quality % number of test files : R²={} and p={}'.format(r2, p))

if __name__ == '__main__':
    java_suite_reg()
    java_smells_reg()

    stars_smells_reg()
    stars_suite_reg()

    issues_suite_reg()
    issues_smells_reg()
