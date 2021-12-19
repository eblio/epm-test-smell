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

def format_user(author):
    return {
        'github_id':author.id,
        'node_id':author.node_id,
        #'contributions':author.contributions,
        'created_at':date_to_str(author.created_at),
        'updated_at':date_to_str(author.updated_at),
        'email':author.email,
        'followers':author.followers,
        'following':author.following,
        'public_gists':author.public_gists,
        'public_repos':author.public_repos,
        'name':author.name,
        'login':author.login,
        'type':author.type
    }

if __name__ == '__main__':
    args = parse_arguments()
    github_api = Github(args.github_token)
    #github_api = Github()
    project_name_pattern = '(?<=^https:\/\/github.com\/)[^\/]+\/[^\/\n\.]+'
    commits_collection = get_database()['commits']
    users_collection = get_database()['users']
    authors_info = commits_collection.aggregate([
        {
            '$match': {
                'user': {
                    '$exists': 0
                },
                'url':{'$regex':'github','$options':'i'}
            }
        },
        {
            '$group': {
                '_id': {'author':'$author','email':'$author_email'},
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
    for author_info in authors_info:
        url = author_info['url']
        logging.info(author_info)
        #Get repo informations if needed
        if(not url in repos):
            repo_name =  re.search(project_name_pattern,url.lower(), re.IGNORECASE)[0]
            repos[url] = github_api.get_repo(repo_name)

        try:
            commit = repos[url].get_commit(sha=author_info['commit'])
            author = commit.author
            if author is None:
                logging.error('No author found for commit {}'.format(author_info['commit']))
                continue
            github_user = format_user(author)
            commits_collection.update_many({'author':author_info['_id']['author'],'author_email':author_info['_id']['email']},{'$set':{'user':github_user}})
        except:
            logging.error('No author found for commit {}'.format(author_info['commit']))
