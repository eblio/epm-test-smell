'''
Extracts issues for a list of repositories.
'''

import time
import json
import argparse
import pandas as pd
from github import Github

OUT_PATH = '../../data/rq1/android_issues/'
PER_REPO_REQUESTS = 500

def parse_args():
    '''
    Creates and parses command line arguments.
    '''
    parser = argparse.ArgumentParser(description='Extract Github project issues.')

    parser.add_argument('-f', '--file', dest='file', help='File containing the repos list.')
    parser.add_argument('-t', '--token', dest='token', help='Github access token.')
    parser.add_argument('-n', '--name', dest='name', help='Repository name to start at.')

    return parser.parse_args()


def name_to_filename(name):
    '''
    Converts a repository name to a JSON file name.
    '''
    return name.replace('/', '-') + '.json' # Transformation asymétrique


def get_issue_data(i):
    '''
    Gets the relevant information from an issue object.
    '''
    return {
        'id': i.id,
        'title': i.title,
        'opened_at': str(i.created_at),
        'closed_at': str(i.closed_at)
    }


def get_issues(r):
    '''
    Gets the issues from the repository.
    '''
    issues = []

    for issue in r.get_issues(state='all'):
        issues.append(get_issue_data(issue))

    return issues


def get_repo_list_issues(file, token, start_name):
    '''
    Gets the repositories issues ans save them as a JSON file.
    '''
    g = Github(token)
    input_file = pd.read_csv(file)
    start = False

    for name in input_file['name']:

        # Skip unwanted repositories
        if name == start_name:
            start = True
        if not start:
            continue
        
        # Check rate limit to avoid undesired expceptions
        current, _ = g.rate_limiting
        print('{} requests left'.format(current))

        if current > PER_REPO_REQUESTS:
            print('Processing {} ...'.format(name))

            # Get the repo data
            r = g.get_repo(name)
            issues = get_issues(r)

            # Save the issues
            with open(OUT_PATH + name_to_filename(name), 'w') as f:
                json.dump(issues, f, indent=4)
        else:
            sleep_time = abs(g.rate_limiting_resettime - time.time() + 10)

            print('Its sleep time ! For : {}s'.format(sleep_time))

            # Sleep until our nulber of request gets restored
            time.sleep(sleep_time)
            g = Github(token)

import os
if __name__ == '__main__':
    # args = parse_args()
    # get_repo_list_issues(args.file, args.token, args.name)
    print(len(os.listdir('../../data/rq1/android_issues')))
