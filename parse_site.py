# methods used to parse the site and get the data
# we want to parse ICLM, ICLR, NeurIPS, TMLR, JMLR

import paper
import requests
from bs4 import BeautifulSoup
import tqdm
import json

def get_papers(search_term, url_getter, url_parser):
    papers = []
    paper_urls = url_getter(search_term)
    print('loading papers ...')
    for url in tqdm.tqdm(paper_urls):
        paper = url_parser(url)
        if paper.valid_paper():
            papers.append(paper)
        else:
            print('Found invalid paper: ', paper)
    return papers

def get_icml_paper_urls(search_term):
    url = 'https://proceedings.mlr.press/'

    # get the page
    page = requests.get(url)
    #print(page.text)
    soup = BeautifulSoup(page.text, 'html.parser')

    # find all li items within the proceedings list
    li_items = soup.find_all('li') if soup else []

    paper_urls = []
    # print each li item
    li_items = [li for li in li_items if 'ICML' in li.text and 'Workshop' not in li.text]
    print('finding paper urls ...')
    for li in tqdm.tqdm(li_items):

        # get the link
        link = li.find('a')
        if link: 
            proceedings_url = url + link.get('href')
            proceedings_page = requests.get(proceedings_url)
            proceedings_soup = BeautifulSoup(proceedings_page.text, 'html.parser')

            # find all paper divs
            paper_divs = proceedings_soup.find_all('div', class_='paper')
    
            for div in paper_divs:
                # find the title of the paper
                title = div.find('p', class_='title').text if div.find('p', class_='title') else ''
                # check if the search term is in the title
                if search_term in title.lower():
                    # find the abstract link
                    abstract_tag = div.find('a', text='abs')
                    if abstract_tag:
                        abstract_link = abstract_tag.get('href')
                        paper_urls.append(abstract_link)

    return paper_urls

def get_neurips_paper_urls(search_term):
    url = 'https://papers.nips.cc/papers/search?q='
    search_term = search_term.replace(' ', '+')
    url += search_term

    # get the page
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    paper_urls = []
    li_items = soup.find_all('li')
    # for each element, get the title, authors, year, venue, doi, url_pdf, abstract
    print("finding paper urls ...")
    for li_item in tqdm.tqdm(li_items):
        link = li_item.find('a')
        if link is not None:
            if 'paper_files' in link.get('href'):
                paper_urls.append(link.get('href'))

    return paper_urls

def get_iclr_paper_urls(search_term):
    years = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    paper_urls = []
    for year in years:
        url = 'https://iclr.cc/virtual/{}/papers.html?filter=titles&search={}'.format(year, search_term.replace(' ', '+'))

        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        li_items = soup.find_all('li')

        # Extract the URLs
        for li_item in li_items:
            #print(search_term, li_item.text.lower())
            if search_term in li_item.text.lower():
                #print(year, li_item.text.lower())
                link = li_item.find('a')
                if link is not None:
                    poster_url = link.get('href')
                    poster_page = requests.get('https://iclr.cc' + poster_url)
                    poster_soup = BeautifulSoup(poster_page.text, 'html.parser')
                    # Find the link with class 'btn btn btn-outline-dark btn-sm href_URL'
                    link = poster_soup.find('a', class_='btn btn btn-outline-dark btn-sm href_URL')

                    # Extract the URL
                    openreview_url = link.get('href') if link else None
                    paper_urls.append(openreview_url)

    return paper_urls

def parse_openreview_paper_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Extract the JSON data from the script tag with id '__NEXT_DATA__'
    script_tag = soup.find('script', id='__NEXT_DATA__')
    data = json.loads(script_tag.string)

    # Extract the required information
    forum_note = data['props']['pageProps']['forumNote']
    title = forum_note['content']['title']
    authors = forum_note['content']['authors']
    venue = forum_note['content']['venue']
    year = forum_note['content']['_bibtex'].split('\n')[4].split('=')[1].strip('{},')  # Extract year from bibtex
    bibtex = forum_note['content']['_bibtex']
    url_pdf = 'https://openreview.net' + forum_note['content']['pdf']  # Prepend the base URL
    abstract = forum_note['content']['abstract']
    
    return paper.Paper(title, authors, year, venue, bibtex, url_pdf, abstract)

def get_tmlr_paper_urls(search_term):
    pass

def get_jmlr_paper_urls(search_term):
    pass

def parse_icml_paper_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # get the title
    title_tag = soup.find('meta', attrs={'name': 'citation_title'})
    title = title_tag.get('content') if title_tag else None

    # get the authors
    author_tags = soup.find_all('meta', attrs={'name': 'citation_author'})
    authors = [tag.get('content') for tag in author_tags] if author_tags else None

    # get the year
    year_tag = soup.find('meta', attrs={'name': 'citation_publication_date'})
    year = year_tag.get('content')[:4] if year_tag else None  # get only the year part

    # get the pdf url
    url_pdf_tag = soup.find('meta', attrs={'name': 'citation_pdf_url'})
    url_pdf = url_pdf_tag.get('content') if url_pdf_tag else None

    # get the abstract
    abstract_tag = soup.find('div', attrs={'class': 'abstract'})
    abstract = abstract_tag.text.strip() if abstract_tag else None

    # get the bibtex
    bibtex_tag = soup.find('code', attrs={'class': 'citecode', 'id': 'bibtex'})
    bibtex = bibtex_tag.text.strip() if bibtex_tag else None

    # venue
    venue = 'icml'

    return paper.Paper(title, authors, year, venue, bibtex, url_pdf, abstract)

def parse_neurips_paper_url(url):
    """Parse the paper from the given url and return a Paper object."""
    url = 'https://papers.nips.cc' + url

    # get the page
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # get the title
    title_tag = soup.find('meta', attrs={'name': 'citation_title'})
    title = title_tag.get('content') if title_tag else None

    # get the authors
    author_tags = soup.find_all('meta', attrs={'name': 'citation_author'})
    authors = [tag.get('content') for tag in author_tags] if author_tags else None

    # get the year
    year_tag = soup.find('meta', attrs={'name': 'citation_publication_date'})
    year = year_tag.get('content')[:4] if year_tag else None  # get only the year part

    # get the pdf url
    url_pdf_tag = soup.find('meta', attrs={'name': 'citation_pdf_url'})
    url_pdf = url_pdf_tag.get('content') if url_pdf_tag else None

    # get the abstract
    abstract_header = soup.find('h4', text='Abstract')
    abstract_tag = abstract_header.find_next_sibling('p') if abstract_header else None
    abstract = abstract_tag.text if abstract_tag else None

    # get the bibtex url
    bibtex_url_tag = soup.find('a', text='Bibtex')
    bibtex_url = bibtex_url_tag.get('href') if bibtex_url_tag else None

    # download the bibtex file
    if bibtex_url:
        bibtex_url = 'https://papers.nips.cc' + bibtex_url
        response = requests.get(bibtex_url)
        bibtex = response.text
    else:
        bibtex = None

    # venue
    venue = 'neurips'

    return paper.Paper(title, authors, year, venue, bibtex, url_pdf, abstract)