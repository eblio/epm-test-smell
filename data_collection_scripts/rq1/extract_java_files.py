'''
Extracts the number of Java files in a project.
'''

import utils
import time
import argparse
import pandas as pd
from github import Github

OUT_FILE = '../../data/rq1/repos_java_files.csv'
PER_REPO_REQUESTS = 100

def parse_args():
    '''
    Creates and parses command line arguments.
    '''
    parser = argparse.ArgumentParser(description='Extract Github project issues.')

    parser.add_argument('-f', '--file', dest='file', help='File containing the repos list.')
    parser.add_argument('-t', '--token', dest='token', help='Github access token.')
    parser.add_argument('-n', '--name', dest='name', help='Repository name to start at.')

    return parser.parse_args()


def is_a_java_file(filename):
    '''
    Checks whether a file is a java file.
    '''
    return filename.endswith('.java')


def get_main_branch_sha(r):
    '''
    Gets the main branch sha (main or master).
    '''
    sha = ''

    for branch in r.get_branches():
        sha = branch.commit.sha

        if branch.name == r.default_branch:
            break

    return sha


def get_number_of_java_files(r):
    '''
    Gets the relevant information from an issue object.
    '''
    java_files = 0
    
    for f in r.get_git_tree(get_main_branch_sha(r), recursive=True).tree:
        if is_a_java_file(f.path):
            java_files += 1

    return java_files
        

def get_repo_data(github, name):
    '''
    Gets the correctly formated repository data.
    '''
    r = github.get_repo(name)

    return {
        'url': r.clone_url,
        'name': name,
        'java_files': get_number_of_java_files(r)
    }


def get_repo_list_java_files(file, token, start_name):
    '''
    Gets the repositories issues ans save them as a JSON file.
    '''
    g = Github(token)
    input_file = pd.read_csv(file)
    output_file = pd.DataFrame()
    start = False

    try:
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
                output_file = output_file.append(get_repo_data(g, name), ignore_index=True)
            else:
                sleep_time = abs(g.rate_limiting_resettime - time.time() + 10)

                print('Its sleep time ! For : {}s'.format(sleep_time))

                # Sleep until our number of request gets restored
                time.sleep(sleep_time)
                g = Github(token)
    except Exception as e:
        print(e)

    output_file.to_csv(OUT_FILE, index=False)


def add_test_files():
    '''
    Adds the number of tests files to the previously gathered number of java files.
    '''
    output_file = pd.read_csv(OUT_FILE)
    test_files = []

    for name in output_file['name']:
        filename = utils.project_name_to_file_name(utils.name_to_project_name(name))
        input_file = pd.read_csv(filename)
        test_files.append(len(input_file['App']))

    output_file = output_file.assign(test_files=pd.Series(test_files).values)
    output_file.to_csv(OUT_FILE + '.out', index=False)


if __name__ == '__main__':
    add_test_files()
    # args = parse_args()
    # get_repo_list_java_files(args.file, args.token, args.name)
