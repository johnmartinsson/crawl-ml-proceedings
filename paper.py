import warnings
import json

class Paper():
    def __init__(self, title, authors, year, venue, bibtex, url_pdf, abstract, accepted):
        self.title = title
        # check if authors is a list
        if isinstance(authors, list):
            authors = json.dumps(authors)

        self.authors = authors
        self.venue = venue
        self.year = int(year)

        self.bibtex = bibtex
        self.url_pdf = url_pdf
        self.abstract = abstract
        self.accepted = accepted

        self.check_supported_types()

    def __str__(self):
        # pad title with spaces up to 100 characters
        #title = self.title.ljust(200)
        venue = self.venue.ljust(7)
        return f"{venue}; {self.year}; {self.title}"
    
    def check_supported_types(self):
        if not isinstance(self.title, str):
            # warning
            warnings.warn(f"Title should be a string, but got {type(self.title)}")
        if not isinstance(self.authors, str):
            warnings.warn(f"Authors should be a string, but got {type(self.authors)}")
        if not isinstance(self.venue, str):
            warnings.warn(f"Venue should be a string, but got {type(self.venue)}")
        if not isinstance(self.year, int):
            warnings.warn(f"Year should be an integer, but got {type(self.year)}")
        if not isinstance(self.bibtex, str):
            warnings.warn(f"Bibtex should be a string, but got {type(self.bibtex)}")
        if not isinstance(self.url_pdf, str):
            warnings.warn(f"url_pdf should be a string, but got {type(self.url_pdf)}")
        if not isinstance(self.abstract, str):
            warnings.warn(f"Abstract should be a string, but got {type(self.abstract)}")
        if not isinstance(self.accepted, bool):
            warnings.warn(f"Accepted should be a boolean, but got {type(self.accepted)}")
        

    def valid_paper(self):
        self.check_supported_types()
        return self.title and self.authors and self.venue and self.year and self.url_pdf and self.abstract and self.bibtex
    
# TODO: maybe implement subclasses for different venues? They have some different information
