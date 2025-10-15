# Security compliance

This repo contains what is necessary to automatically scan, detect and alert users about npm packages impacted by vulnerabilities.

# Structure
```
security-clearance/
├── data/
│   └── vulnerable_packages.json
├── scripts/
│   └── inspect_npm_packages.py
│   └── scrape_html_table.py
├── notes/
│   └── info.md
├── .github/
│   └── workflows/
│       └── automate_script.yml
└── README.md
```
where:
- `vulnerable_packages.json`: json file containing all vulnerable npm packages and versions
- `inspect_npm_packages.py`: the python script run by the Github Action, taking care of inspecting all repos in the organisation and looking for dependencies that are 
- `scrape_html_table.py`: a script to automatically export the table in the aikido.dev website into a json file (needs to be run from the parent directory `security-clearance/`)
- `automate_script.yml`: the workflow file used by the Github Action to automate the python script 
- `info.md`: an example of how this situation would be communicated to users in the company, it would be shared (e.g. via mail marked as urgent) as soon as possible  
- `README.md`: what you are reading right now!
