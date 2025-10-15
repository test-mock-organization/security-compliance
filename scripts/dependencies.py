"""
This file contains the function to scan dependencies in a repo
we can define it for any arbitrary language ecosystem, here we do it for 2 popular languages: JavaScript and Python
to do so, we have helper functions that can parse the files accordingly
"""

import os
import json
import re
import toml

# helper functions to parse different file formats

# JavaScript: package.json
def parse_package_json(content):
    data = json.loads(content)
    deps = {}
    for section in ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies']:
        for pkg, ver in data.get(section, {}).items():
            deps[pkg] = ver
    return deps

# Python: requirements.txt
def parse_requirements_txt(content):
    deps = {}
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            match = re.match(r'^([\w\-\_]+)([<>=!~]=?.*)?', line)
            if match:
                pkg, ver = match.groups()
                deps[pkg] = ver.strip() if ver else '*'
    return deps

# Python: Pipfile
def parse_pipfile(content):
    deps = {}
    pipfile = toml.loads(content)
    for section in ['packages', 'dev-packages']:
        for pkg, ver in pipfile.get(section, {}).items():
            if isinstance(ver, dict):
                deps[pkg] = ver.get('version', '*')
            else:
                deps[pkg] = ver
    return deps

# Python: pyproject.toml
def parse_pyproject_toml(content):
    deps = {}
    data = toml.loads(content)
    poetry = data.get('tool', {}).get('poetry', {})
    for section in ['dependencies', 'dev-dependencies']:
        for pkg, ver in poetry.get(section, {}).items():
            if pkg.lower() == 'python':
                continue
            if isinstance(ver, dict):
                deps[pkg] = ver.get('version', '*')
            else:
                deps[pkg] = ver
    return deps

# Python: setup.py
def parse_setup_py(content):
    deps = {}
    matches = re.findall(r'install_requires\s*=\s*\[([^\]]+)\]', content, re.DOTALL)
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

    # for each file name/format we now have the proper helper functions to parse it!
    expected_files = {
        'package.json': parse_package_json,
        'requirements.txt': parse_requirements_txt,
        'Pipfile': parse_pipfile,
        'pyproject.toml': parse_pyproject_toml,
        'setup.py': parse_setup_py,
    }

    try:
        # we assume that the dependencies informations lies at the root of the repo
        root_files = repo.get_contents("/")
    except Exception as e:
        print(f"Failed to read repository root: {e}")
        return dependencies

    for file in root_files:
        # we look at all file in the root
        if file.name in expected_files:
            try:
                content = file.decoded_content.decode('utf-8')

                # we use the above dict to find the correct parser to read the content
                parser = expected_files[file.name]
                parsed = parser(content)

                dependencies.update(parsed)

            except Exception as e:
                print(f"Error parsing {file.name}: {e}")

    return dependencies
