# crawl-ml-proceedings
A tool to crawl machine learning proceedings for abstracts, pdfs, key words, bibtex et cetera.

# How to use

    python3 crawl.py --venue=iclr --search_term='active learning'

This will crawl 'iclr' for papers with 'active learning' in the title and insert them into papers.db.

__supported venues__: iclr (back to 2018), iclm (back to 2013), neurips (back to 1988)

Do this for all venues if you want papers from all of them.

    python find_papers.py

This will rank all the abstracts with the predefined abstract in find_papers.py, change to one of your own abstracts.
