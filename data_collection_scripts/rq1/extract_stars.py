'''
Extracts the stars from a repository list.
'''

import utils
import math
import argparse
import pandas as pd
from github import Github

OUT_FILE = '../../data/rq1/repos_stars.csv'

def parse_args():
    '''
    Creates and parses command line arguments.
    '''
    parser = argparse.ArgumentParser(description='Extract Github project informations.')

    parser.add_argument('-f', '--file', dest='file', help='File containing the repos list.')
    parser.add_argument('-t', '--token', dest='token', help='Github access token.')

    return parser.parse_args()


def get_repo_data(github, name):
    '''
    Gets the repository data.
    '''
    r = github.get_repo(name)

    return {
        'url': r.clone_url,
        'name': name,
        'stars': int(r.stargazers_count),
        'log_stars': math.log10(r.stargazers_count + 1) # log10(s + 10) gives worse results reagrding readability of the hist
    }


def get_repo_list_data(token, file):
    '''
    Gets the repositories in the file data.
    '''
    input_data = pd.read_csv(file)
    output_data = pd.DataFrame()

    g = Github(token)

    for url in input_data['url']:
        if utils.is_github_repo(url):
            print('Processing {} ...'.format(url))
            name = utils.github_url_to_name(url)
            output_data = output_data.append(get_repo_data(g, name), ignore_index=True)

    output_data.to_csv(OUT_FILE, index=False)


if __name__ == '__main__':
    args = parse_args()
    get_repo_list_data(args.token, args.file)
