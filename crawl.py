import os
import parse_site as ps
import argparse

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
        ps.parse_iclr()
    elif args.venue == 'tmlr':
        ps.parse_tmlr()
    elif args.venue == 'jmlr':
        ps.parse_jmlr()
    else:
        print('Venue not supported')

    # print the papers
    print("number of papers: ", len(papers))


if __name__ == '__main__':
    main()