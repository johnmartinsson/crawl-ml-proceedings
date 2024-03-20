import os
import parse_site as ps
import argparse
import sqlite3
from functools import partial

def main():
    # parse the arguments
    parser = argparse.ArgumentParser(description='Crawl machine learning proceedings for papers')
    parser.add_argument('--search_term', type=str, help='The search term for the papers')
    parser.add_argument('--venue', type=str, help='The venue to search for the papers in')
    args = parser.parse_args()

    search_term = args.search_term
    search_term = search_term.lower()

    # crawl
    if args.venue == 'neurips':
        papers = ps.get_papers(search_term, ps.get_neurips_paper_urls, ps.parse_neurips_paper_url)
    elif args.venue == 'icml':
        papers = ps.get_papers(search_term, ps.get_icml_paper_urls, ps.parse_icml_paper_url)
    elif args.venue == 'iclr':
        #years = [2018, 2019, 2020, 2021]
        years = [2022, 2023]
        papers = []
        for year in years:
            # ICLR is wierd, so we need to use partial functions and create a new function for each year
            _papers = ps.get_papers(search_term, partial(ps.get_iclr_paper_ids, year=year), partial(ps.parse_openreview_paper_id, venue='iclr', year=year))
            papers.extend(_papers)
    elif args.venue == 'tmlr':
        ps.parse_tmlr()
    elif args.venue == 'jmlr':
        ps.parse_jmlr()
    else:
        print('Venue not supported')

    # store the paper in the database
    conn = sqlite3.connect('papers.db')
    c = conn.cursor()
    # Create table
    c.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            title TEXT UNIQUE,
            authors TEXT,
            venue TEXT,
            year INTEGER,
            bibtex TEXT,
            url_pdf TEXT,
            abstract TEXT,
            search_term TEXT,
            accepted BOOLEAN DEFAULT FALSE
        )
    """)
    # store papers in a database
    print('inserting papers in the database ...')
    for paper in papers:
        if paper.valid_paper():
            print(paper)
            c.execute("""
                INSERT OR REPLACE INTO papers 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (paper.title, ", ".join(paper.authors), paper.venue, paper.year, paper.bibtex, paper.url_pdf, paper.abstract, search_term, paper.accepted))
            conn.commit()
    conn.close()

    # print the papers
    print("number of papers: ", len(papers))


if __name__ == '__main__':
    main()