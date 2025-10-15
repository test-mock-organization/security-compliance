import requests
from bs4 import BeautifulSoup
import json
import os 

URL = "https://www.aikido.dev/blog/s1ngularity-nx-attackers-strike-again"

# fetch the whole web page
response = requests.get(URL)
response.raise_for_status()

# parse HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# find the table body 
table_body = soup.find('tbody')

# dictionary to hold the extracted data
data = {}

# loop through all table rows in tbody
for row in table_body.find_all('tr'):
    cols = row.find_all('td')
    if len(cols) >= 2:
        package = cols[0].get_text(strip=True)
        version = cols[1].get_text(strip=True)
        data[package] = [version]  # wrap the version in a list for proper format

# we want to store it in /data
output_file = os.path.join('data', 'vulnerable_packages.json')

# save the result to a JSON file
with open(output_file, 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, indent=4, ensure_ascii=False)

print("Data saved to auto_vulnerable_packages.json")