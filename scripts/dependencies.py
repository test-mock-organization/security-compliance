"""
This file contains the function to scan dependencies in a repo
we can define it for any arbitrary language ecosystem, here we do it for 2 popular languages: JavaScript and Python
to do so, we have helper functions that can parse the files accordingly
"""

import os
import json
import re
import toml
import requests
import re

# helper functions to parse different file formats

# JavaScript: package.json
def get_dependencies_from_package_json(repo):
    try:
        file = repo.get_contents("package.json")
        response = requests.get(file.download_url)
        if response.status_code == 200:
            package_json = json.loads(response.text)
            deps = {}
            for section in ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies']:
                deps.update(package_json.get(section, {}))
            return deps
    except:
        pass
    return {}

# Python: requirements.txt
def get_dependencies_from_requirements_txt(repo):
    try:
        file = repo.get_contents("requirements.txt")
        response = requests.get(file.download_url)
        if response.status_code == 200:
            deps = {}
            for line in response.text.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    match = re.match(r'^([\w\-\_]+)([<>=!~]=?.*)?', line)
                    if match:
                        pkg, ver = match.groups()
                        deps[pkg] = ver.strip() if ver else '*'
            return deps
    except:
        pass
    return {}

# Python: Pipfile
def get_dependencies_from_pipfile(repo):
    try:
        file = repo.get_contents("Pipfile")
        response = requests.get(file.download_url)
        if response.status_code == 200:
            pipfile = toml.loads(response.text)
            deps = {}
            for section in ['packages', 'dev-packages']:
                for pkg, ver in pipfile.get(section, {}).items():
                    if isinstance(ver, dict):
                        deps[pkg] = ver.get('version', '*')
                    else:
                        deps[pkg] = ver
            return deps
    except:
        pass
    return {}

# Python: pyproject.toml
def get_dependencies_from_pyproject_toml(repo):
    try:
        file = repo.get_contents("pyproject.toml")
        response = requests.get(file.download_url)
        if response.status_code == 200:
            pyproject = toml.loads(response.text)
            poetry = pyproject.get('tool', {}).get('poetry', {})
            deps = {}
            for section in ['dependencies', 'dev-dependencies']:
                for pkg, ver in poetry.get(section, {}).items():
                    if pkg.lower() == 'python':
                        continue
                    if isinstance(ver, dict):
                        deps[pkg] = ver.get('version', '*')
                    else:
                        deps[pkg] = ver
            return deps
    except:
        pass
    return {}

# Python: setup.py
def get_dependencies_from_setup_py(repo):
    try:
        file = repo.get_contents("setup.py")
        response = requests.get(file.download_url)
        if response.status_code == 200:
            setup_code = response.text
            deps = {}
            matches = re.findall(r'install_requires\s*=\s*\[([^\]]+)\]', setup_code, re.DOTALL)
            for match in matches:
                lines = match.split(',')
                for line in lines:
                    line = line.strip().strip("'\"")
                    if line:
                        pkg_match = re.match(r'^([\w\-\_]+)([<>=!~]=?.*)?', line)
                        if pkg_match:
                            pkg, ver = pkg_match.groups()
                            deps[pkg] = ver.strip() if ver else '*'
            return deps
    except:
        pass
    return {}

# main function
def scan(repo):
    """
    Given a repository, gives all packages required by a repository as a dictionary
    
    Parameter:
        repo (github.Repository.Repository): Github repository
    
    Returns:
        dependencies (dict): all dependencies in repo (as keys) with their allowed version range (as values)
    """
    dependencies = {}

    dependencies.update(get_dependencies_from_package_json(repo))
    dependencies.update(get_dependencies_from_requirements_txt(repo))
    dependencies.update(get_dependencies_from_pipfile(repo))
    dependencies.update(get_dependencies_from_pyproject_toml(repo))
    dependencies.update(get_dependencies_from_setup_py(repo))

    return dependencies
