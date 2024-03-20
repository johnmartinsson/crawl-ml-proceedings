class Paper():
    def __init__(self, title, authors, year, venue, bibtex, url_pdf, abstract):
        self.title = title
        self.authors = authors
        self.venue = venue
        self.year = year

        self.bibtex = bibtex
        self.url_pdf = url_pdf
        self.abstract = abstract

    def __str__(self):
        return f"{self.title} by {self.authors} in {self.venue} ({self.year})"
    
    def valid_paper(self):
        return self.title and self.authors and self.venue and self.year and self.url_pdf and self.abstract and self.bibtex