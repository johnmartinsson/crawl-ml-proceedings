import requests
from bs4 import BeautifulSoup

import argparse

def main():
    parser = argparse.ArgumentParser(description='Get page and save to file')
    parser.add_argument('--url', type=str, help='The url to get')
    parser.add_argument('--file', type=str, help='The file to save the page to')
    args = parser.parse_args()


    url = args.url
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    with open(args.file, 'w') as f:
        f.write(soup.prettify())

def get_page(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup

if __name__ == '__main__':
    main()