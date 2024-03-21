# Crawl ICLR, ICML, NeurIPS and arXiv
A tool to crawl machine learning proceedings for abstracts, pdfs, key words, bibtex et cetera and populate a database with these. Then match the abstracts of the papers in the database against one of your own abstracts and rank by similarity.

# How to use

    python3 crawl.py --venue=arxiv --query_term='"active learning"' --database=papers.db

This will crawl 'arxiv' for papers with "active learning" in the title and insert them into papers.db. The query functionality is limited, but just keep to lower case characters and use the same format as above and it should be fine. It can handle

    '"words to match" AND "otherword"'

which will make sure that "words to match" appears as is in the title of the paper, and that "otherword" appears in the title. (I hope.)

supported venues: 
- iclr, back to 2018,
- iclm, back to 2013,
- neurips, back to 1988
- arxiv

Run this command for all venues and query_terms that you want to use to crawl papers, with the same --database=papers.db command, and it will be populated with all papers you want.

ICLR constrains the number of queries, so this takes time if you have many hits. It is also a bit buggy still and may crash.

# Rank abstract similarity to a pre-defined weighted sentence list

    python find_papers.py --database=papers.db --random_papers=0 --sentence_list_name=default

This will rank all the abstracts with the predefined weighted sentences in the sentence list "detault" in find_papers.py, change to your liking to get relevant hits. If you set --random_papers > 0 a random selection of all papers will be chosen for the ranking. Can be good when building a new sentence list to iterate quickly and get a feeling for what type of matches it produces.
