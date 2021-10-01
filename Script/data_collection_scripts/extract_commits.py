import re
import requests
import subprocess
import json
import os
import shutil
import argparse
from pydriller import Repository
from datetime import datetime

def get_project_name(repo_url):
    '''
    Extracts the project name.
    '''
    return os.path.basename(repo_url[:-4])


def extract_commits(repo_url, clean_up):
    '''
    Extracts all the commits from a repository given certain criteria.
    '''

    start_time = datetime.now()
    project_info = dict()
    project_name = get_project_name(repo_url)
    project_dir = "repo/{}".format(project_name)

    #Clone repo if needed
    print("Cloning repository {}".format(project_name))
    if not os.path.isdir(project_dir):
        subprocess.run(["git","clone", repo_url, project_dir])

    print("Creating repository object {}".format(project_name))
    repo = Repository(project_dir,
                      only_modifications_with_file_types = ".java",
                      since=datetime(2021, 1, 1))

    print("Start commit analysis")

    for commit_hash in repo.get_tagged_commit(): # TODO: test
        commit = repo.get_commit(commit_hash)
        commit_diff = dict()

        for modified_file in commit.modified_files:
            #No added modifications
            if not modified_file.filename.endswith(".java") or not modified_file.diff_parsed['added']:
                continue

            #Store file modfications
            commit_diff[modified_file.filename] = modified_file.diff_parsed['added']
        #Store commit modifications
        if commit_diff:
            project_info[str(commit.hash)] = commit_diff
    if clean_up:
        shutil.rmtree(project_dir)

    print('Time elapsed (hh:mm:ss.ms) {}'.format(datetime.now() - start_time))

    return project_info


def extract_projects(repo_list_path, repo_folder_path, clean_up = False):
    '''
    Processes the projects.
    '''
    projects = dict()

    with open('repo.txt') as f:
        url = [x.rstrip() for x in f.readlines()]

        for repo_url in url:
            project_name = get_project_name(repo_url)
            projects[project_name] = extract_commits(repo_url,clean_up)
            print("{} analysis complete".format(project_name))

    return projects

def write_data():
    '''
    Writes extracted data to a file.
    '''
    repo_list_path = '../data/repo_index.txt'
    repo_folder_path = '../data/repositories'
    p = extract_projects(repo_list_path, repo_folder_path, False)
    file = 'data.json'
    os.remove(file)

    with open(file, "w") as f:
        json.dump(p, f, indent = 6)
