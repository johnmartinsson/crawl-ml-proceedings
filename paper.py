class Paper():
    def __init__(self, title, authors, year, venue, bibtex, url_pdf, abstract, accepted):
        self.title = title
        self.authors = authors
        self.venue = venue
        self.year = year

        self.bibtex = bibtex
        self.url_pdf = url_pdf
        self.abstract = abstract
        self.accepted = accepted

    def __str__(self):
        # pad title with spaces up to 100 characters
        #title = self.title.ljust(200)
        venue = self.venue.ljust(7)
        return f"{venue}, {self.year}, {self.title}"
    
    def valid_paper(self):
        return self.title and self.authors and self.venue and self.year and self.url_pdf and self.abstract and self.bibtex
    
# TODO: maybe implement subclasses for different venues? They have some different information