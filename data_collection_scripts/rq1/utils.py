'''
Utility functions.
'''

import re

GITHUB_URL_TO_NAME = '(?<=^https:\/\/github.com\/)[^\/]+\/[^\/\n]+'
GITHUB_URL = 'https://github'

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
