import argparse
import translate_files
import traceback
import os
import re
import datetime
import shutil
import logging
import subprocess
import json
import pandas as pd
from pydriller import Repository

logging.basicConfig(filename='test_smells_detection.log', encoding='utf-8', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract information related to test smells')
    subparsers = parser.add_subparsers()
    commitParser = subparsers.add_parser('commit')
    commitParser.add_argument('-i', '--repositories_csv', dest='input_csv', help='Repositories .csv from mine_repos.py')
    commitParser.add_argument('-r', '--repositories_folder', dest='repositories_folder', help='Folder use to clone repositories')
    commitParser.add_argument('-t', '--tools_folder', dest='tools_folder', help='Folder containing all tools')
    commitParser.set_defaults(func=run_smells_history_analysis)
    return parser.parse_args()

def get_all_files_by_pattern(regex, parent='.'):
    regex = re.compile(regex)
    files_with_pattern = []
    for _, _, files in os.walk(parent):
        for file in files:
            if regex.match(file):
                files_with_pattern.append(file)
    return files_with_pattern


def get_file_by_pattern(regex, parent='.'):
    regex = re.compile(regex)
    for _, _, files in os.walk(parent):
        for file in files:
            if regex.match(file):
                return file

def remove_csv_files():
    regex = re.compile('.*\.csv')
    for _, _, files in os.walk("."):
        for file in files:
            if regex.match(file):
                os.remove(file)

def clone_repository(repo_info, keep_history):
    repo_info['path'] = os.path.join(args.repositories_folder, repo_info['name'])
    if not os.path.isdir(repo_info['path']):
        if keep_history:
            subprocess.run(["git","clone", repo_info['url'], repo_info['path']])
        else:
            subprocess.run(["git","clone", repo_info['url'], repo_info['path'], '--depth', '1'])
    else:
        logging.info('{} already clone'.format(repo_info['name']))

def detect_repository_tests_files(repo_info):
    wd = os.getcwd()
    os.chdir(repo_info['path'])
    commit_hash = subprocess.run(['git', 'rev-parse', 'HEAD'],capture_output=True).stdout.decode().strip()
    os.chdir(wd)
    subprocess.run(['java', '-jar',  os.path.join(args.tools_folder,'TestFileDetector.jar'), repo_info['path'], repo_info['name'], commit_hash])
    detector_output_file = translate_files.test_detection_to_mapping(get_file_by_pattern('Output_Class_.*\.csv'))
    subprocess.run(['java', '-jar', os.path.join(args.tools_folder,'TestFileMapping.jar'), detector_output_file, repo_info['name'], commit_hash])
    mapping_output_file = translate_files.mapping_to_smell_detection(get_file_by_pattern('Output_TestFileMappingDetection_.*\.csv'))

    smells_file = 'smells_{}_{}.csv'.format(repo_info['name'], commit_hash)
    subprocess.run(['java', '-jar', os.path.join(args.tools_folder,'TestSmellDetector.jar'), '-f', mapping_output_file, '-g', 'numerical', '-o', smells_file])
    data = pd.read_csv(smells_file)
    remove_csv_files()
    return data


def get_relevant_commits(repo_info):
    wd = os.getcwd()
    os.chdir(repo_info['path'])
    commits_info = dict()
    commits = subprocess.run(['git', 'log', '--all', '--pretty=%H,%at,%ct,%an,%cn,%f,%ce,%ae'],capture_output=True).stdout.decode().strip().split('\n')
    for commit in commits:
        fields = commit.split(',')
        if fields[0]  in commits_info:
            continue
        commits_info[fields[0]] = { 'author_timestamp':fields[1],
                                    'commiter_timestamp':fields[2],
                                    'author':fields[3],
                                    'commiter':fields[4],
                                    'subject':fields[5],
                                    'commiter_email':fields[6],
                                    'author_email':fields[7]}
    os.chdir(wd)
    return commits_info


def analyse_commit(repo_info,commit_hash, commit_info, wd):
    os.chdir(repo_info['path'])
    subprocess.run(['git', 'checkout', commit_hash])
    os.chdir(wd)
    test_smells_report = detect_repository_tests_files(repo_info)
    json_report = json.loads(test_smells_report.to_json(orient='records'))
    return {'hash':commit_hash,
                            'author_timestamp':commit_info['author_timestamp'],
                            'commiter_timestamp':commit_info['commiter_timestamp'],
                            'author':commit_info['author'],
                            'commiter':commit_info['commiter'],
                            'subject':commit_info['subject'],
                            'app':repo_info['name'],
                            'url':repo_info['url'],
                            'detection':json_report}



def get_database():
    from pymongo import MongoClient
    import pymongo
    client = MongoClient("mongodb://localhost:27018")
    return client['epm-test-smell']


def get_commit_diff(repo_info, commit_hash):
    for commit in Repository(repo_info['path'], single=commit_hash).traverse_commits():
        commit_diff = dict()
        for modified_file in commit.modified_files:
            if not modified_file.filename.endswith(".java"):
                continue

            #Store file modfications
            commit_diff[modified_file.filename] = modified_file.diff_parsed
        #Store commit modifications
        return commit_diff



def run_smells_history_analysis():
    wd = os.getcwd()
    commits_collection = get_database()['commits']
    repositories = pd.read_csv(args.input_csv)
    for _, repo_info in repositories.iterrows():
        try:
            logging.info('{}: cloning'.format(repo_info['name']))
            clone_repository(repo_info, True)

            logging.info('{}: extracting relevant commits'.format(repo_info['name']))
            commits_info = get_relevant_commits(repo_info)

            logging.info('{}: analysing {} commits'.format(repo_info['name'],len(commits_info)))
            for i,commit_hash in enumerate(commits_info):
                logging.info('{}: commit #{}'.format(repo_info['name'],i))
                if commits_collection.find({'hash':commit_hash, 'app':repo_info['name']}).count() > 0:
                    logging.info('{}: skipping commit #{}'.format(repo_info['name'],i))
                    continue
                commit_report = analyse_commit(repo_info, commit_hash, commits_info[commit_hash], wd)
                commit_report['diff'] = get_commit_diff(repo_info, commit_hash)
                commits_collection.insert_one(commit_report)
        except Exception:
            logging.error('{}: error during analysis'.format(repo_info['name']))
            traceback.print_exc()

if __name__ == '__main__':
    args = parse_arguments()
    args.func()
