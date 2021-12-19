'''
Utility functions.
'''

import glob
import re

GITHUB_URL_TO_NAME = '(?<=^https:\/\/github.com\/)[^\/]+\/[^\/\n]+'
GITHUB_URL = 'https://github'
SMELL_PATH = '../../data/rq1/android_test_smells/'
NAME_FORMAT = '*_{}_*.csv'

def is_github_repo(url):
    '''
    Gets whether the repository is hosted on Github or not.
    '''
    return GITHUB_URL in url


def github_url_to_name(url):
    '''
    Gets the repository name (user/project_name) from the URL.
    '''
    name = re.search(GITHUB_URL_TO_NAME, url)[0]
    return name[:len(name) - 4]  # Remove the .git


def name_to_project_name(name):
    '''
    Gets the project name based on the repository name (user/project).
    '''
    return name.split("/", 1)[1].replace('/', '_')


def project_name_to_file_name(name):
    '''
    Gets the file corresponding to a certain project name.
    '''
    return glob.glob(SMELL_PATH + NAME_FORMAT.format(name))[0]
