import os
import json
from datetime import datetime, timezone
from github import Github, Auth

# since the version of packages is in general given as a range (using ^, ~, >, <, =) we need semantic_version to treat that 
from semantic_version import SimpleSpec, Version

# we can write a general function to scan for dependencies in another file to keep it general and not restrict to a language ecosystem
import dependencies

# we load the GH token from environment (to avoid hardcoding it here!)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = "test-mock-organization"

# open file where vulnerable packages are defined with vulnerable versions
vulnerable_packages_file = os.path.join("data", "vulnerable_packages.json")
with open(vulnerable_packages_file, "r") as f:
    VULNERABLE_PACKAGES = json.load(f)

# define the issue title + content, this is what the users will see
ISSUE_TITLE = "Vulnerable dependencies detected"
ISSUE_BODY_TEMPLATE = """This repository uses one or more packages with known issues or vulnerabilities:

{}

Please review and update these dependencies if appropriate.
"""

# maximum number of days we leave an open Issue before acting on it 
MAXIMUM_DAYS = 1

# GH API client
auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)
org = g.get_organization(ORG_NAME)

# we maybe do not want to inspect all repositories so we can exclude some by name
exclude_names = {"security-compliance"}
repos = [repo for repo in org.get_repos() if repo.name not in exclude_names]

# function to check whether a package and range is vulnerable
def is_version_vulnerable(pkg, allowed_range):
    """
    By looking at a package and its version string (using ^, ~, >, <, =), we compare it to the dict of known vulnerable packages
    (if the vulnerable version is contained in the allowed range, we are in trouble)
    
    Parameters:
        pkg (string): package name
        allowed_range (string): version string, contains all the different versions of that package that is allowed by the project 
    
    Returns:
        (boolean): is it vulnerable
    """
    if pkg not in VULNERABLE_PACKAGES:
        # package clean
        return False
    
    try:
        # here we use the semantic_version library to see if that package is contained in the range
        spec = SimpleSpec(allowed_range)
        for vuln_ver_str in VULNERABLE_PACKAGES[pkg]:
            # convert string to Version object
            vuln_version = Version(vuln_ver_str)
            # if the vulnerable version is allowed by the range, there is a problem
            if vuln_version in spec:
                return True
        return False  # none of the vulnerable versions are included
    
    except Exception as e:
        print(f"Error checking version for {pkg}: {e}")
        return False

# function to raise the GH issue in a given repo with its vulnerable dependencies
def create_issue(repo, vulnerable_deps):
    """
    Create a Github Issue with vulnerable dependencies in the body
    
    Parameters:
        repo (github.Repository.Repository): Github repository
        vulnerable_deps (dict): dependencies that we want to inform the users about
    """    
    # find all open issues with the same title
    existing_issues = []
    for issue in repo.get_issues(state='open'):
        if ISSUE_TITLE.lower() in issue.title.lower():
            existing_issues.append(issue)
    
    # format the body for the new vulnerabilities
    new_body = ISSUE_BODY_TEMPLATE.format("\n".join(f"- `{pkg}@{ver}`" for pkg, ver in vulnerable_deps.items()))
    
    # check if any existing issue has the same body
    for issue in existing_issues:
        if issue.body.strip() == new_body.strip():  # ignore leading/trailing whitespace
            print("No new vulnerabilities to report. Issue already exists.")
            return  # no new issue created, as the body is the same

    # if no matching issue is found, create a new issue with updated list of vulnerable dependencies
    try:
        repo.create_issue(title=ISSUE_TITLE, body=new_body)
        print(f"Created new issue in {repo.full_name}")
    except Exception as e:
        print(f"Failed to create issue in {repo.full_name}: {e}")

# main loop
for repo in repos:
    print(f"Checking {repo.full_name}...")

    # all dependencies in the repo
    deps = dependencies.scan(repo)

    # this will contain all the vulnerable dependencies used in that repo
    vulnerable_deps = {}

    for pkg, version in deps.items():
        if is_version_vulnerable(pkg, version):
            vulnerable_deps[pkg] = version

    # in case there are vulnerable dependencies, then we raise the alarm by creating an issue!
    if vulnerable_deps:
        create_issue(repo, vulnerable_deps)

    # now we want to follow up on issues that are already open since a specific amount of time
    open_issues = repo.get_issues(state="open")
    for issue in open_issues:
        # if it is an issue raised by this script then it has the title ISSUE_TITLE 
        # (we dont want to act on other Issues, possibly opened by users manually)
        if ISSUE_TITLE in issue.title:
            age_days = (datetime.now(timezone.utc) - issue.created_at).days
            if age_days >= MAXIMUM_DAYS:

                # we insert a marker in the comment so that we can easily know that it is not written by a user
                marker = "<!-- generated reminder comment -->"
                
                # comment content
                reminder_comment = f"{marker}\nThis issue has been open for {age_days} days... Please review the dependencies!"
                
                # we want to check if we already commented this one to not spam every time the script runs!
                # get the first generated comment with next(...), we assume there is only 1 per post anyways
                comments = issue.get_comments()
                bot_comment = next((c for c in comments if marker in c.body), None)

                if bot_comment:
                    # edit the existing comment
                    bot_comment.edit(reminder_comment)
                    print(f"Updated comment on {repo.full_name}#{issue.number}")
                else:
                    # create a new comment if none found
                    issue.create_comment(reminder_comment)
                    print(f"Posted new comment on {repo.full_name}#{issue.number}")
                
                # also add a label if not already present
                labels = [label.name for label in issue.labels]
                if "overdue" not in labels:
                    issue.add_to_labels("overdue")