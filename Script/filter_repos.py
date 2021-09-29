IN_FILE = './JupyterData/'
OUT_FILE = './JupyterData/'

with open(IN_FILE, 'r') as f:
    for repo_url in f:
        print(repo_url)
        # TODO : 
        #   - Filter on number of stars (?)
        #   - Filter on amount of tag (1, 2 ?..)
        #   - Filter on existing gits
        #   - Check paper filtering
