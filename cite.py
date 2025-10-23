import requests
from bs4 import BeautifulSoup
import csv

# search terms you are looking for
search_terms = [ "password"]

# read in URLs from a .csv file
csv_file = input("Enter the CSV filename containing URLs: ").strip()
urls = []
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'url' in row and row['url']:
            urls.append(row['url'])

found_urls = []
for url in urls:
    try:
        # get page content
        response = requests.get(url, timeout=10)
        # exception for bad status (4xx or 5xx)
        response.raise_for_status()

        # parse html
        soup = BeautifulSoup(response.text, 'html.parser')

        # extract all readable text from body of page
        page_text = soup.get_text()

        # search text for keywords
        found_keywords = [term for term in search_terms if term.lower() in page_text.lower()]

        # output findings
        if found_keywords:
            print(f"Found keywords on: {url}")
            print(f"   Keywords found: {', '.join(found_keywords)}\n")
            found_urls.append(url)
        else:
            print(f" No specific keywords found on: {url}\n")

    except requests.exceptions.RequestException as e:
        print(f"Could not access {url}. Error: {e}\n")

# print urls where keywords were found
if found_urls:
    print("\nSummary: Keywords found on the following URLs:")
    for u in found_urls:
        print(u)
else:
    print("\nSummary: No keywords found on any URL.")