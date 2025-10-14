import os
import json
import requests
from github import Github
# since the version of packages is in general given as a range (using ^, ~, >, <, =) we need semantic_version to treat that 
from semantic_version import SimpleSpec, Version

# we load the GH token from environment (to avoid hardcoding it here!)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = "test-mock-organization"

# define vulnerable packages with vulnerable versions
VULNERABLE_PACKAGES = {
    "ngx-perfect-scrollbar": "20.0.20",
    "config-eslint": ">2.0.4"
}

# define the issue title + content, this is what the users will see
ISSUE_TITLE = "Vulnerable NPM dependencies detected"
ISSUE_BODY_TEMPLATE = """This repository uses one or more npm packages with known issues or vulnerabilities:

{}

Please review and update these dependencies if appropriate.
"""

# GH API client
g = Github(GITHUB_TOKEN)
org = g.get_organization(ORG_NAME)
repos = org.get_repos()

# find the package json file in a repo
def get_package_json(repo):
    try:
        file = repo.get_contents("package.json")
        response = requests.get(file.download_url)
        # we check that the request has succeeded (200 = OK)
        if response.status_code == 200:
            return json.loads(response.text)
    except:
        pass
    return None

# given a package in a json format, we extract all dependencies
def extract_dependencies(package_json):
    all_deps = {}
    # those are the fields for the packages needed to run the app or for development etc...
    for section in ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies']:
        deps = package_json.get(section, {})
        all_deps.update(deps)
    return all_deps

# by looking at a package and its version string, we compare it to the dict of known vulnerable packages
def is_version_vulnerable(pkg, version_str):
    if pkg not in VULNERABLE_PACKAGES:
        # package clean
        return False
    try:
        # here we use the semantic_version library to see if that package is contained in the range
        spec = SimpleSpec(VULNERABLE_PACKAGES[pkg])
        clean_version = version_str.lstrip("^~<>= ")
        version = Version.coerce(clean_version)
        return version in spec
    except Exception:
        return False
    
# we want a way to check whether we already raised the issue in a given repo
def issue_already_exists(repo):
    try:
        for issue in repo.get_issues(state='open'):
            # we check by looking at the title (what about the body?)
            if ISSUE_TITLE.lower() in issue.title.lower():
                return True
    except:
        pass
    return False

# function to raise the GH issue in a given repo with its vulnerable dependencies
def create_issue(repo, vulnerable_deps):
    # we use the template defined above
    body = ISSUE_BODY_TEMPLATE.format("\n".join(f"- `{pkg}@{ver}`" for pkg, ver in vulnerable_deps.items()))
    try:
        repo.create_issue(title=ISSUE_TITLE, body=body)
        print(f"Created issue in {repo.full_name}")
    except Exception as e:
        print(f"Failed to create issue in {repo.full_name}: {e}")

# main loop
for repo in repos:
    print(f"Checking {repo.full_name}...")
    package_json = get_package_json(repo)
    if not package_json:
        # there is no package.json file
        continue

    # all dependencies in the repo
    deps = extract_dependencies(package_json)

    # this will contain all the vulnerable dependencies used in that repo
    vulnerable_deps = {}

    for pkg, version in deps.items():
        if is_version_vulnerable(pkg, version):
            vulnerable_deps[pkg] = version

    # in case there are vulnerable dependencies, then we raise the alarm!
    if vulnerable_deps:
        if not issue_already_exists(repo):
            create_issue(repo, vulnerable_deps)
        else:
            print(f"Issue already exists in {repo.full_name}!")