# methods used to parse the site and get the data
# we want to parse ICLM, ICLR, NeurIPS, TMLR, JMLR

import paper
import requests
from bs4 import BeautifulSoup
import tqdm
import json
import time
from datetime import datetime, timezone

def matches_query(query, text):
    # Split the query into terms by 'AND'
    terms = query.split(' AND ')

    terms = [term.strip('"') for term in terms]

    # For each term
    for term in terms:
        # Split the term into subterms by '+'
        subterms = term.split('+')

        # Check if all subterms are in the text
        if not all(subterm in text for subterm in subterms):
            # If any subterm is not in the text, the whole query does not match
            return False

    # If we got here, all terms and subterms are in the text
    return True

def get_response(url):
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()  # This will raise an exception for 4xx and 5xx status codes
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.text:  # Check if the response is not empty
                error_data = e.response.json()
                
                if error_data.get('name') == 'RateLimitError':
                    reset_time_str = error_data['details']['resetTime']
                    # Parse the ISO 8601 string and convert it to a timestamp
                    reset_time = datetime.strptime(reset_time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc).timestamp()
                    # Calculate how long to wait until the rate limit resets
                    wait_time = max(0, (reset_time - time.time()) + 1)  # Add 1 second to be safe
                    print(f"Rate limit error. Waiting {wait_time:.2f} seconds until {reset_time_str}...")
                    time.sleep(wait_time)
                else:
                    raise  # Re-raise the exception if it's not a rate limit error
            else:
                raise  # Re-raise the exception if the response is empty

def get_papers(query_term, url_getter, url_parser):
    papers = []
    paper_urls = url_getter(query_term)
    print('loading papers ...')
    for url in tqdm.tqdm(paper_urls):
        try:
            paper = url_parser(url)
            if paper.valid_paper():
                papers.append(paper)
            else:
                print('Found invalid paper: ', paper)
        except Exception as e:
            print('Error parsing paper: ', url)
    return papers

###############################################################################
# Url getters
###############################################################################

def get_arxiv_paper_ids(query_term):
    paper_chunks = 200
    #url = f"https://arxiv.org/search/?query={query_term}&searchtype=all&source=header&order=-announced_date_first&size={paper_chunks}&abstracts=show&date-date_type=submitted_date&start={start_chunk}"
    url = f"https://arxiv.org/search/?query={query_term}&searchtype=title&abstracts=show&order=-announced_date_first&size={paper_chunks}"
    print(url)

    done = False
    ids = []
    while not done:
        # get the page
        page = get_response(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        # Find all 'a' tags with 'href' starting with "https://arxiv.org/abs"
        links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('https://arxiv.org/abs')]
        # Extract the arXiv ID from the URL
        ids.extend([link.split('/')[-1] for link in links])

        # get the next page
        next_url = soup.find('a', class_='pagination-next')
        if next_url:
            url = 'https://arxiv.org' + next_url['href']
        else:
            done = True

    return ids


def get_icml_paper_urls(query_term):
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
                if matches_query(query_term, title.lower()):
                    # find the abstract link
                    abstract_tag = div.find('a', text='abs')
                    if abstract_tag:
                        abstract_link = abstract_tag.get('href')
                        paper_urls.append(abstract_link)

    return paper_urls

def get_neurips_paper_urls(query_term):
    url = 'https://papers.nips.cc/papers/search?q='
    url += query_term

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
                paper_urls.append('https://papers.nips.cc' + link.get('href'))

    return paper_urls

def get_iclr_paper_ids(query_term, year='2023'):
    venue = 'ICLR.cc/{}/Conference'.format(year)
    def get_conference_notes(venue, blind_submission=False):
        """
        Get all notes of a conference (data) from OpenReview API.
        If results are not final, you should set blind_submission=True.
        """
        blind_param = '-/Blind_Submission' if blind_submission else ''
        offset = 0
        notes = []
        while True:
            #print('Offset:', offset, 'Data:', len(notes))
            url = f'https://api.openreview.net/notes?invitation={venue}/{blind_param}&offset={offset}'
            response = requests.get(url)
            data = response.json()
            if len(data['notes']) == 0:
                break
            offset += 1000
            notes.extend(data['notes'])
        return notes

    raw_notes = get_conference_notes(venue, blind_submission=True)
    
    paper_ids = []
    for note in raw_notes:
        title = note['content']['title']
        if matches_query(query_term, title.lower()):
            paper_ids.append(note['id'])
    
    return paper_ids


def get_tmlr_paper_urls(query_term):
    pass

def get_jmlr_paper_urls(query_term):
    pass

###############################################################################
# Url parsers
###############################################################################

def get_arxiv_paper_url_and_year(id):
    # check if id format yy.mmnnnn (post 2007) or yymmnnn (pre 2007)
    if '.' in id:
        # post 2007 identifier scheme, yymm.nnnn
        url = f'https://arxiv.org/abs/{id}'
        # Extract the year and month from the arXiv ID
        year, _ = id.split('.')[:2]

        # The year is the first two digits of the arXiv ID
        year = '20' + year[:2]
    else:
        # pre 2007 identifier scheme, yymmnnn
        url = f'https://arxiv.org/abs/cs/{id}'
        # Extract the year from the arXiv ID
        yy = int(id[:2])
        
        # WARNING: This will map papers from 1900-1907 to 2000-2007
        if yy > 7:
            year = '19' + id[:2]
        else:
            year = '20' + id[:2]

    return url, year

def parse_arxiv_paper_id(id):
    url, year = get_arxiv_paper_url_and_year(id)

    #try:
    page = get_response(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # Find the elements containing the required information
    title_element = soup.find('h1', class_='title mathjax')
    authors_element = soup.find('div', class_='authors')
    abstract_element = soup.find('blockquote', class_='abstract mathjax')
    pdf_link_element = soup.find('a', attrs={'accesskey': 'f'})

    # Extract the text from the elements
    title = title_element.text.replace('Title: ', '') if title_element else None
    authors = authors_element.text.replace('\n', ' ').replace('Authors:', '').strip() if authors_element else None
    abstract = abstract_element.text.replace('\n', ' ').replace('Abstract: ', '').strip() if abstract_element else None
    url_pdf = 'https://arxiv.org' + pdf_link_element['href'] if pdf_link_element else None
    venue = 'arxiv'

    # Construct the URL for the BibTeX citation page
    bibtex_url = f'https://arxiv.org/bibtex/{id}'
    # Send a GET request to the URL
    response = requests.get(bibtex_url)
    # The content of the response is the BibTeX citation
    bibtex = response.text



    # assume false for all arxiv papers
    accepted = False

    return paper.Paper(title, authors, year, venue, bibtex, url_pdf, abstract, accepted)

def parse_icml_paper_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # pretty print the soup to file
    with open('icml.html', 'w') as f:
        f.write(soup.prettify())


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

    return paper.Paper(title, authors, year, venue, bibtex, url_pdf, abstract, accepted=True)

def parse_neurips_paper_url(url):
    """Parse the paper from the given url and return a Paper object."""

    # get the page
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # pretty print the soup to file
    with open('nips.html', 'w') as f:
        f.write(soup.prettify())

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

    return paper.Paper(title, authors, year, venue, bibtex, url_pdf, abstract, accepted=True)

def parse_openreview_paper_id(id, venue, year):
    # OpenReview API has a rate limit of 100 requests per minute

    url = f"https://api.openreview.net/notes?forum={id}"

    response = get_response(url)
    data = response.json()

    notes = data.get('notes')
    if notes is not None:
        #print(json.dumps(notes, indent=4))
        accepted = False
        for note in notes:
            #print(json.dumps(note, indent=4))
            decision = note['content'].get('decision')
            if decision is not None:
                if 'accept' in decision.lower():
                    accepted = True
                    break
    else:
        print(json.dumps(data, indent=4))
    
    url = f"https://openreview.net/forum?id={id}"
    page = get_response(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # pretty print the soup to file
    with open('iclr.html', 'w') as f:
        f.write(soup.prettify())

    # Extract the JSON data from the script tag with id '__NEXT_DATA__'
    script_tag = soup.find('script', id='__NEXT_DATA__')
    data = json.loads(script_tag.string)

    # Extract the required information
    forum_note = data['props']['pageProps']['forumNote']
    title = forum_note['content']['title']
    authors = forum_note['content']['authors']
    venue = venue
    year = year
    bibtex = forum_note['content']['_bibtex']
    url_pdf = 'https://openreview.net' + forum_note['content']['pdf']  # Prepend the base URL
    abstract = forum_note['content']['abstract']
    
    return paper.Paper(title, authors, year, venue, bibtex, url_pdf, abstract, accepted)