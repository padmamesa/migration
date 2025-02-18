#!/usr/bin/env python

__author__ = "PadmaMesa"
__copyright__ = "Copyright 2025, Padma Mesa"
__license__ = "ex"
__version__ = "1.0.0"
__maintainer__ = "Padma Mesa"
__email__ = "padma.mesa@gmail.com"

import os
import shutil
import gitlab
from github import Github

gitlab_cred = { 
   'user': 'xxxxxxx',
   'pass': 'xxxxxxxx',
   'token': 'xxxxxxxxxxxxxxxx',
   'host': 'https://gitlab.xxxxxxxxxxx.com'
}
github_cred = {
   'token': 'xxxxxxxxxxxxxxxxxxxxxxxxxxx',
}

def gitclone(path, url):
    repo_dir = os.path.join(".", path)
    if os.path.isdir(repo_dir): 
        shutil.rmtree(repo_dir)       
    if os.system("git clone --mirror {} {} > /dev/null 2>&1".format(url, repo_dir)) != 0:
        return False
    return True

def gitpush(path, url):
    repo_dir = os.path.join(".", path)
    os.chdir(repo_dir)
    if os.system("git push --no-verify --mirror {}  > /dev/null 2>&1".format(url)) != 0:
        return False
    return True

gitlab = gitlab.Gitlab(gitlab_cred["host"], token=gitlab_cred["token"]) 
# The gitlab object is created in the script with the connection details (gitlab_cred), 
# which means it's authenticated with the GitLab server.
g = Github(github_cred["token"])
g_user = g.get_user()

total = []
migrated = []
skipped = []
failed = []

# The loop for project in gitlab.getall(gitlab.getprojects): iterates over each repository (project) returned by gitlab.getall(gitlab.getprojects). 
# Each project is a dictionary containing the details of a GitLab repository (such as the name, description, and the repository's URL).
# Inside the loop, various actions are performed:
# The script extracts the repository’s details, such as path (the name of the repository) and description.
# It checks whether the repository already exists on GitHub.
# It clones the repository from GitLab to the local machine.
# It creates a new repository on GitHub and pushes the cloned repository there.

# gitlab.getall(gitlab.getprojects): This is a method call that fetches a list of all projects (repositories) from GitLab.
for project in gitlab.getall(gitlab.getprojects):  # gitlab.getprojects is likely a method (or API endpoint) that retrieves the list of projects from GitLab.
    http_url_to_repo = project["http_url_to_repo"].split("://")
    path = project["path"].lower()
    description = project["description"]
    total.append(path)
    try:
        if g_user.get_repo(path):
            print("WARN: Repository {} already present on Github".format(path))
            skipped.append(path)
            continue
    except:
        pass
    
    print("INFO: Cloning repo {}".format(path))
    if not gitclone(path, "{}://{}:{}@{}".format(http_url_to_repo[0], gitlab_cred["user"], gitlab_cred["pass"], http_url_to_repo[1])): 
        print("ERR: Failed during cloning {}".format(path))
        failed.append(path)
        continue
    
    print("INFO: Creating new repo {} on github".format(path))
    try:
        g_repo = g_user.create_repo(path, description=description, private=True)
    except Exception as ex: 
        print("ERR: Failed during creation of repo {} in github: {}".format(path, ex.message))
        failed.append(path)
        continue

    print("INFO: Pushing repo {} on github".format(path))
    if not gitpush(path, g_repo.ssh_url):
        print("ERR: Failed pushing {} on github".format(path))
        failed.append(path)
        continue

print("#########################")
print("### Migration Summary ###")
print("#########################")
print("Total repo: {}".format(len(total)))
print("Skipped repo: {}".format(len(skipped)))
print("Failed repo: {}".format(len(failed)))
for r in failed:
    print("> {}".format(r))
print("#########################")
