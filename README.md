# Security compliance

This repo contains what is necessary to automatically scan, detect and alert users about packages impacted by vulnerabilities.

# Structure
```
security-clearance/
├── data/
│   └── vulnerable_packages.json
├── scripts/
│   └── inspect_packages.py
│   └── dependencies.py
│   └── scrape_html_table.py
├── notes/
│   └── info.md
├── .github/
│   └── workflows/
│       └── automate_script.yml
└── README.md
```
where:
- `vulnerable_packages.json`: json file containing all vulnerable packages and versions
- `inspect_packages.py`: the python script run by the Github Action, taking care of inspecting all repos in the organisation and looking for dependencies that are 
- `dependencies.py`: where we define what kind of dependencies we are looking for, basically a general function that is used in `inspect_packages.py` and can be adapted to any language ecosystem
- `scrape_html_table.py`: a script to automatically export the table in the aikido.dev website into a json file (needs to be run from the parent directory `security-clearance/`)
- `automate_script.yml`: the workflow file used by the Github Action to automatically run the python script 
- `info.md`: an example of how this situation would be communicated to users in the company, it would be shared (e.g. via mail marked as urgent) as soon as possible  
- `README.md`: what you are reading right now!

# Course of events

So what does the code do ?

1) In a scheduled (or manually triggered) Github Action, a Python script will automatically inspect at regular intervals all relevant repositories within the organization and look for all the dependencies used in each repository.
2) By comparing it to a list of known vulnerable packages (which can be either defined by hand or automatically scraped from a website), it will raise a Github Issue in respective repositories where the vulnerable packages are used, informing the users of which packages are problematic for them.
3) If the issue is not solved and closed within 1 day, the script will add a comment within that issue and label it as 'overdue'. This comment will be updated accordingly to track by how much time it is overdue.