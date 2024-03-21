import sqlite3
from transformers import AutoTokenizer, AutoModel
import torch
from paper import Paper

import tqdm
import argparse
import random

from multiprocessing import Pool

def get_sentence_list(name):
    """
    Get a weighted list of sentences to compare title and abstract to in embedding space. The weight indicates the relative importance of the sentence.

    Args:
    name (str): The name of the sentence list to get.

    Returns:
    list: A list of [(weight, sentence)] tuples.
    """
    if name == 'default':
        return [
            (1, "From Weak to Strong Sound Event Labels using Adaptive Change-Point Detection and Active Learning"),
        ]
    elif name == 'multi_annotator':
        return [
            (1, "We study the active learning setting where multiple annotators are available to label data"),
            (1, "The annotators have different levels of expertise."),
            (1, "We consider sound event datasets where the annotators can give either weak or strong labels"),
            (1, "The annotators can give either weak labels or strong labels for the unlabeled audio recording"),
        ]
    elif name == 'time_frequency':
        return [
            (1, "In this paper we present the differentiable log-Mel spectrogram (DMEL) for audio classification."),
            (1, "DMEL uses a Gaussian window, with a window length that can be jointly optimized with the neural network."),
            (1, "DMEL is used as the input layer in different neural networks and evaluated on standard audio datasets."),
            (1, "We show that DMEL achieves a higher average test accuracy for sub-optimal initial choices of the window length when compared to a baseline with a fixed window length."),
            (1, "In addition, we analyse the computational cost of DMEL and compare to a standard hyperparameter search over different window lengths, showing favorable results for DMEL."),
            (1, "Finally, an empirical evaluation on a carefully designed dataset is performed to investigate if the differentiable spectrogram actually learns the optimal window length."),
            (1, "The design of the dataset relies on the theory of spectrogram resolution. We also empirically evaluate the convergence rate to the optimal window length.")
        ]
    elif name == 'decentralized_learning':
        return [
            (1, "Personalized decentralized learning is a promising paradigm for distributed learning, enabling each node to train a local model on its own data and collaborate with other nodes to improve without sharing any data."),
            (1, "However, this approach poses significant privacy risks, as nodes may inadvertently disclose sensitive information about their data or preferences through their collaboration choices."),
            (1, "In this paper, we propose Private Personalized Decentralized Learning (PPDL), a novel approach that combines secure aggregation and correlated adversarial multi-armed bandit optimization to protect node privacy while facilitating efficient node selection."),
            (1, "By leveraging dependencies between different arms, represented by potential collaborators, we demonstrate that PPDL can effectively identify suitable collaborators solely based on aggregated models."),
            (1, "Additionally, we show that PPDL surpasses previous non-private methods in model performance on standard benchmarks under label and covariate shift scenarios."),
        ]
    else:
        raise ValueError(f"Unknown sentence list: {name}")

def main():
    parser = argparse.ArgumentParser(description='Find similar papers')
    parser.add_argument('--database', type=str, help='The database to search for papers')
    parser.add_argument('--random_papers', type=int, help='The number of random papers to select', default=0)
    
    # list of [(weight, sentence)]
    parser.add_argument('--sentence_list_name', type=str, help='Name of the sentence list to compare with', default='')
    args = parser.parse_args()

    # Connect to the SQLite database
    conn = sqlite3.connect(args.database)
    c = conn.cursor()

    # Select all papers
    c.execute("SELECT * FROM papers")

    # Fetch all the rows
    data = c.fetchall()

    papers = []
    for d in data:
        papers.append(Paper(title=d[0], authors=d[1], venue=d[2], year=d[3], bibtex=d[4], url_pdf=d[5], abstract=d[6], accepted=d[7]))

    # Close the connection
    conn.close()

    print("number of papers: ", len(papers))
    if args.random_papers > 0:
        papers = random.sample(papers, args.random_papers)

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
    # abstract = "In this work we propose an audio recording segmentation method based on an adaptive change point detection (A-CPD) for machine guided weak label annotation of audio recording segments. The goal is to maximize the amount of information gained about the temporal activation's of the target sounds. For each unlabeled audio recording, we use a prediction model to derive a probability curve used to guide annotation. The prediction model is initially pre-trained on available annotated sound event data with classes that are disjoint from the classes in the unlabeled dataset. The prediction model then gradually adapts to the annotations provided by the annotator in an active learning loop. The queries used to guide the weak label annotator towards strong labels are derived using change point detection on these probabilities. We show that it is possible to derive strong labels of high quality even with a limited annotation budget, and show favorable results for A-CPD when compared to two baseline query strategies."

    # title = "From Weak to Strong Sound Event Labels using Adaptive Change-Point Detection and Active Learning"

    #abstract_embedding = encode(abstract).squeeze()
    #title_embedding = encode(title).squeeze()

    sentence_list = get_sentence_list(args.sentence_list_name)
    sentence_embedding = None
    for sentence in sentence_list:
        weight, text = sentence
        if sentence_embedding is not None:
            # TODO: not sure how to combine the embeddings
            sentence_embedding = sentence_embedding + weight * encode(text).squeeze()
        else:
            sentence_embedding = weight * encode(text).squeeze()
    sentence_embedding = sentence_embedding / sum([weight for weight, _ in sentence_list])
        
    # IDEAS
    # parallelize the computation of the similarities and append to a list

    similarities = []
    for paper in tqdm.tqdm(papers):
        if paper.accepted:
            other_abstract = paper.abstract
            other_title = paper.title

            other_abstract_embedding = encode(other_abstract).squeeze()
            other_title_embedding = encode(other_title).squeeze()
            
            # TODO: not sure how to combine the two embeddings
            other_embedding = 0.5 * other_abstract_embedding + 0.5 * other_title_embedding
            similarity = torch.nn.functional.cosine_similarity(sentence_embedding, other_embedding, dim=0).item()
            
            similarities.append((paper, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    with open('similar_papers.txt', 'w') as f:
        f.write("similarity;venue;year;title;authors;url\n")
        for paper, similarity in similarities:
            # write to a file
            f.write(f"{similarity:.3f};{paper.venue};{paper.year};{paper.url_pdf};{paper.title};{paper.authors}\n")

            # print to the console
            #print(f"{similarity:.3f};{paper.venue};{paper.year};{paper.title}")

if __name__ == '__main__':
    main()
