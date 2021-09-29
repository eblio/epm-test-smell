IN_FILE = './JupyterData/'
OUT_FILE = './JupyterData/'

with open(IN_FILE, 'r') as f:
    for repo_url in f:
        print(repo_url)

