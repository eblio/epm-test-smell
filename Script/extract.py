import re
import requests
import subprocess
import json
import os
import shutil
from pydriller import Repository
from datetime import datetime

def find_repos():
    '''
    Finds the repositories from previously extracted apk names.
    This function is no longer used as we found a better way to extract repos.
    '''

    with open('known_apks.txt', 'r') as f:
        githubApks = set()
        invalid = set()
        line = f.readline()
        while line:
            if "github" in line.lower():
                m = re.search("\w*\.\w*(?=_)", line)
                if m and "github" not in m.group():
                    apk = m.group().split('.')
                    url = 'https://github.com/{}/{}.git\n'.format(apk[0], apk[1])
                    if url not in githubApks and url not in invalid:
                        try:
                            r = requests.get(url)
                            if r.status_code == 200:
                                print('✅ {}'.format(url))
                                githubApks.add(url)
                            else:
                                invalid.add(url)
                                print('❌ {}'.format(url))
                        except requests.ConnectionError:
                            print('Github error'.format(url))
            line = f.readline()

    file = 'githubapk.txt'

    if os.path.isfile(file):
        os.remove(file)
    with open(file) as f2:
        f2.writelines(githubApks)

# def parse_fdroid(path):
#     with open('{}_parse'.format(path), 'x') as out:
#         with open(path, 'r') as f:
#             archive_apks = set()
#             invalid = set()
#             line = f.readline()
#             while line:
#                 m = re.search("\w*\.\w*(?=_\d)", line)
#                 if m:
#                     apk = m.group().split('.')
#                     urlGithub = 'https://github.com/{}/{}.git\n'.format(apk[0], apk[1])
#                     if urlGithub not in archive_apks and urlGithub not in invalid:
#                         try:
#                             r = requests.get(urlGithub)
#                             if r.status_code == 200:
#                                 #print('✅ {}'.format(urlGithub))
#                                 archive_apks.add(urlGithub)                                
#                                 out.write(urlGithub)
#                             else:
#                                 invalid.add(urlGithub)
#                                 #print('❌ {}'.format(urlGithub))
#                         except requests.ConnectionError:
#                             print('Github error'.format(urlGithub))
#                     urlGitlab = 'https://gitlab.com/{}/{}.git\n'.format(apk[0], apk[1])
#                     if urlGitlab not in archive_apks and urlGitlab not in invalid:
#                         try:
#                             r = requests.get(urlGitlab)
#                             if r.status_code == 200:
#                                 #print('✅ {}'.format(urlGitlab))
#                                 archive_apks.add(urlGitlab)
#                                 out.write(urlGitlab)
#                             else:
#                                 invalid.add(urlGitlab)
#                                 #print('❌ {}'.format(urlGitlab))
#                         except requests.ConnectionError:
#                             print('Gitlab error'.format(urlGitlab))
#                 line = f.readline()


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
    for commit in repo.traverse_commits(): # TODO: tags
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


def extract_projects(clean_up = False):
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
    p = extract_projects(False)
    file = 'data.json'
    os.remove(file)

    with open(file, "w") as f:
        json.dump(p, f, indent = 6)

