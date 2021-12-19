import argparse
import os
import logging
import re
import time
from dateutil import parser
from github import Github

logging.basicConfig(encoding='utf-8', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


def date_to_str(date):
    return date.strftime("%Y-%m-%d %H:%M:%S")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract github and gitlab project informations.')
    parser.add_argument('-t', '--github-token', dest='github_token', help='Github access token')
    return parser.parse_args()

def get_database():
    from pymongo import MongoClient
    import pymongo
    client = MongoClient("mongodb://localhost:27018")
    return client['epm-test-smell']

def format_user(commiter):
    return {
        'github_id':commiter.id,
        'node_id':commiter.node_id,
        #'contributions':commiter.contributions,
        'created_at':date_to_str(commiter.created_at),
        'updated_at':date_to_str(commiter.updated_at),
        'email':commiter.email,
        'followers':commiter.followers,
        'following':commiter.following,
        'public_gists':commiter.public_gists,
        'public_repos':commiter.public_repos,
        'name':commiter.name,
        'login':commiter.login,
        'type':commiter.type
    }

if __name__ == '__main__':
    args = parse_arguments()
    github_api = Github(args.github_token)
    #github_api = Github()
    project_name_pattern = '(?<=^https:\/\/github.com\/)[^\/]+\/[^\/\n\.]+'
    commits_collection = get_database()['commits']
    commiters_info = commits_collection.aggregate([
        {
            '$match': {
                'users.committer': {
                    '$exists': 0
                },
                'url':{'$regex':'github','$options':'i'}
            }
        },
        {
            '$group': {
                '_id': {'commiter':'$commiter','email':'$commiter_email'},
                'commit': {
                    '$first': '$hash'
                },
                'url': {
                    '$first': '$url'
                }
        }
    }
    ])
    repos = dict()
    for commiter_info in commiters_info:
        url = commiter_info['url']
        logging.info(commiter_info)
        #Get repo informations if needed
        if(not url in repos):
            repo_name =  re.search(project_name_pattern,url.lower(), re.IGNORECASE)[0]
            repos[url] = github_api.get_repo(repo_name)

        try:
            commit = repos[url].get_commit(sha=commiter_info['commit'])
            commiter = commit.committer
            if commiter is None:
                logging.error('No commiter found for commit {}'.format(commiter_info['commit']))
                continue
            github_user = format_user(commiter)
            commits_collection.update_many({'commiter':commiter_info['_id']['commiter'],'commiter_email':commiter_info['_id']['email']},{'$set':{'users.committer':github_user}})
        except:
            logging.error('No commiter found for commit {}'.format(commiter_info['commit']))
