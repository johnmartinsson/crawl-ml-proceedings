import sqlite3
from transformers import AutoTokenizer, AutoModel
import torch
from paper import Paper

import tqdm

def main():
    # Connect to the SQLite database
    conn = sqlite3.connect('papers.db')
    c = conn.cursor()

    # Select all papers
    c.execute("SELECT * FROM papers")

    # Fetch all the rows
    data = c.fetchall()

    papers = []
    for d in data:
        papers.append(Paper(title=d[0], authors=d[1].split(', '), venue=d[2], year=d[3], bibtex=d[4], url_pdf=d[5], abstract=d[6]))

    # Close the connection
    conn.close()

    print("number of papers: ", len(papers))


    # Load the BERT model
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
    model = AutoModel.from_pretrained('bert-base-uncased')

    # Function to encode text
    def encode(text):
        inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            representations = model(**inputs, output_hidden_states=True)
        # Use the average of the last layer representations as sentence embedding
        sentence_embedding = representations.hidden_states[-1].mean(dim=1).squeeze()
        return sentence_embedding

    # Calculate the cosine similarity between two abstracts
    abstract1 = "In this work we propose an audio recording segmentation method based on an adaptive change point detection (A-CPD) for machine guided weak label annotation of audio recording segments. The goal is to maximize the amount of information gained about the temporal activation's of the target sounds. For each unlabeled audio recording, we use a prediction model to derive a probability curve used to guide annotation. The prediction model is initially pre-trained on available annotated sound event data with classes that are disjoint from the classes in the unlabeled dataset. The prediction model then gradually adapts to the annotations provided by the annotator in an active learning loop. The queries used to guide the weak label annotator towards strong labels are derived using change point detection on these probabilities. We show that it is possible to derive strong labels of high quality even with a limited annotation budget, and show favorable results for A-CPD when compared to two baseline query strategies."
    embedding1 = encode(abstract1).squeeze()

    similarities = []
    for paper in tqdm.tqdm(papers):
        abstract2 = paper.abstract
        embedding2 = encode(abstract2).squeeze()

        cosine_similarity = torch.nn.functional.cosine_similarity(embedding1, embedding2, dim=0).item()
        similarities.append((paper, cosine_similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    for paper, similarity in similarities:
        print(paper, similarity)

if __name__ == '__main__':
    main()