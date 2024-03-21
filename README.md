# Crawl ICLR, ICML, NeurIPS and arXiv
A tool to crawl machine learning proceedings for abstracts, pdfs, key words, bibtex et cetera and populate a database with these. Then match the abstracts of the papers in the database against one of your own abstracts and rank by similarity.

# How to use

    python3 crawl.py --venue=arxiv --query_term='"active learning"' --database=papers.db

This will crawl 'arxiv' for papers with "active learning" and "sound" in the title and insert them into papers.db. The query functionality is very limited, but just keep to lower case characters and use the same format as above and it should be fine.

supported venues: 
- iclr, back to 2018,
- iclm, back to 2013,
- neurips, back to 1988
- arxiv

Run this command for all venues and query_terms that you want to use to crawl papers, with the same --database=papers.db command, and it will be populated with all papers you want.

ICLR constrains the number of queries, so this takes time if you have many hits. It is also a bit buggy still and may crash.

# Rank abstract similarity to own abstract

    python find_papers.py

This will rank all the abstracts with the predefined abstract in find_papers.py, change to one of your own abstracts for relevant results.
