import argparse
import csv
import re
import os
from github import Github

def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract github and gitlab project informations.')
    parser.add_argument('-l', '--list', dest='repos_list_path', help='List of all repository url path')
    parser.add_argument('-o', '--out', dest='out', help='Output .csv path')
    parser.add_argument('-t', '--github-token', dest='github_token', help='Github access token')
    parser.add_argument('-g', '--gitlab-token', dest='gitlab_token', help='Gitlab access token')
    return parser.parse_args()

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

def get_default_info(url):
    info = dict()
    info['url'] = url[:-1]
    info['stars'] = ''
    info['open_issues'] = ''
    info['name'] = ''
    return info


def extract_repo_informations(url, github_api, gitlab_api):
    info = get_default_info(url)
    if is_host_on_gitlab(url):
        pass
    if is_host_on_github(url):
        project = re.search('(?<=^https:\/\/github.com\/)[^\/]+\/[^\/\n]+', url)[0]
        print("project {}".format(project))
        repo = github_api.get_repo(project)
        info['open_issues'] = len(list(repo.get_issues(state='open')))
        info['stars'] = repo.stargazers_count
        info['name'] = repo.name
        print(info)
    return info

def extract_repos_informations():
    args = parse_arguments()
    github_api = Github(args.github_token)
    csv_exists = os.path.isfile(args.out)
    with open(args.repos_list_path, 'r') as f:
        for i,url in enumerate(f.readlines()):
            info = extract_repo_informations(url, github_api, "")
            append_to_csv(args.out,info, i == 0 and not csv_exists)

extract_repos_informations()
