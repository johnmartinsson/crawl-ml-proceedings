
#!/bin/bash

# Define an array of query terms
query_terms=(
    "noisy labels"
    "noisy annotations"
    "partial labels"
    "partial annotations"
    "weak labels"
    "weak annotations"
)

# Venues to crawl
venues=(
    "neurips"
    "icml"
    "iclr"
)

# Loop over each query term and run the crawl.py script
for term in "${query_terms[@]}"; do
    for venue in "${venues[@]}"; do
	# papers with the query term in title are added to the database
        python3 crawl.py --query_term="$term" --database=databases/noisy_labels.db --venue="$venue"
    done
done
