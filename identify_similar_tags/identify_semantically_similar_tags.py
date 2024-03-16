import openai
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine

def read_and_clean_tags(file_path: str) -> list:
    """Read tags from a file and remove the hashtag symbol."""
    with Path(file_path).open('r', encoding='utf-8') as file:
        tags = [(line
                 .strip()
                 .lstrip('#')
                 .replace("/", ", ")
                 .replace("_", " ")
                 .lower()) for line in file]
               
    return tags

def generate_embedding(tag: str) -> dict:
    """Generate embeddings for a list of tags."""
    response = openai.Embedding.create(input=[tag],model="text-embedding-3-large")
    return {tag: np.array(response['data'][0]['embedding'])}

def embed_tags(tags: list, project_path: str) -> dict:
    embeddings_file_path = f"{project_path}tag_embeddings.npz"
    try:
        tag_embeddings_raw = np.load(embeddings_file_path, allow_pickle=True)
        tag_embeddings = {tag: tag_embeddings_raw[tag] for tag in tag_embeddings_raw.files}
        tag_embeddings_raw.close()
        print("file previously calculated embeddings found, using that and only embedding tags not found")
    except FileNotFoundError:
        tag_embeddings = {}

    new_tags = set(tags)-set(tag_embeddings.keys())
    if new_tags:
        for tag in new_tags:
            print(tag)
            embedding_dict = generate_embedding(tag)
            tag_embeddings.update(embedding_dict)
        
        np.savez(embeddings_file_path, **tag_embeddings) # update my doc of tag embeddings    
    
    return tag_embeddings

def calculate_cosine_distances(embeddings: dict):

    results = []

    keys = list(embeddings.keys())
    for i in range(len(keys)-1):
        for j in range(i+1, len(keys)):
            key1, key2 = keys[i], keys[j]
            embedding1, embedding2 = embeddings[key1], embeddings[key2]
            distance = cosine(embedding1, embedding2)
            results.append({'key1': key1, 'key2': key2, 'cosine_distance': distance})

    return pd.DataFrame(results)

if __name__ == "__main__":
    openai.api_key = 'PLACE KEY HERE'
    project_path = "PLACE FILE PATH HERE"

    tags_file_path = f"{project_path}tags.txt"
    tags = read_and_clean_tags(tags_file_path)

    tag_embeddings = embed_tags(tags, project_path)

    cosine_distances = calculate_cosine_distances(tag_embeddings)
    cosine_distances.to_csv(f"{project_path}cosine_distances.csv",index=False)
    print(cosine_distances.nsmallest(n=20, columns="cosine_distance"))
