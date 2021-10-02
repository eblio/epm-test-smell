import argparse
import csv
import re
import os
import logging
import time
from dateutil import parser
from github import Github
from gitlab import Gitlab

logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract github and gitlab project informations.')
    parser.add_argument('-l', '--list', dest='repos_list_path', help='List of all repository url path')
    parser.add_argument('-o', '--out', dest='out', help='Output .csv path')
    parser.add_argument('-t', '--github-token', dest='github_token', help='Github access token')
    parser.add_argument('-g', '--gitlab-token', dest='gitlab_token', help='Gitlab access token')
    return parser.parse_args()

def date_to_str(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

def is_host_on_github(url):
    return "https://github" in url

def is_host_on_gitlab(url):
    return "https://gitlab" in url

def append_to_csv(path, info, include_headers = False):
    with open(path, 'a') as f:
        w = csv.DictWriter(f, info.keys())
        if include_headers:
            w.writeheader()
        w.writerow(info)

def get_default_info():
    info = dict()
    info['url'] = ''
    info['stars'] = ''
    info['open_issues'] = ''
    info['commits_count'] = ''
    info['forks_count'] = ''
    info['last_commit_date'] = ''
    info['created_at'] = ''
    info['name'] = ''
    return info

def set_gitlab_info(info, gitlab_api, project_name):
    repo = gitlab_api.projects.get(project_name)
    info['url'] = repo.http_url_to_repo
    info['open_issues'] = repo.open_issues_count
    info['stars'] = repo.star_count
    info['name'] = repo.name
    info['created_at'] = date_to_str(parser.parse(repo.created_at))
    info['forks_count'] = repo.forks_count
    commits = repo.commits.list(all=True)
    info['commits_count'] = len(commits)
    info['last_commit_date'] = date_to_str(parser.parse(commits[0].created_at))

def set_github_info(info, github_api, project_name):
    repo = github_api.get_repo(project_name)
    info['url'] = repo.clone_url
    info['open_issues'] = len(list(repo.get_issues(state='open')))
    info['stars'] = repo.stargazers_count
    info['name'] = repo.name
    info['forks_count'] = repo.forks_count
    commits = repo.get_commits()
    info['commits_count'] = commits.totalCount
    info['created_at'] = date_to_str(repo.created_at)
    info['last_commit_date'] = date_to_str(commits[0].commit.author.date)


def extract_repo_informations(url, github_api, gitlab_api):
    project_name_pattern = '(?<=^https:\/\/{}\/)[^\/]+\/[^\/\n]+'
    info = get_default_info()
    if is_host_on_gitlab(url):
        set_gitlab_info(info, gitlab_api, re.search(project_name_pattern.format('gitlab.com'),url)[0])
    if is_host_on_github(url):
        set_github_info(info, github_api, re.search(project_name_pattern.format('github.com'), url)[0])
    return info

def extract_repos_informations():
    args = parse_arguments()
    github_api = Github(args.github_token)
    gitlab_api = Gitlab('https://gitlab.com', private_token=args.gitlab_token)
    gitlab_api.auth()
    csv_exists = os.path.isfile(args.out)
    is_first_project = True
    with open(args.repos_list_path, 'r') as f:
        for url in f.readlines():
            logging.info('Extracting informations for {}'.format(url[:-1]))
            try:
                info = extract_repo_informations(url, github_api, gitlab_api)
                if info['url']:
                    append_to_csv(args.out,info, is_first_project and not csv_exists)
                    is_first_project = False
            except:
                logging.error('Error extracting informations for {}'.format(url[:-1]))

extract_repos_informations()
