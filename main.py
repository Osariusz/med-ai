import json
import time

import numpy as np
import pandas as pd
import requests
import redis
from redis.commands.search.field import (
    NumericField,
    TagField,
    TextField,
    VectorField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from sentence_transformers import SentenceTransformer

PARAGRAPH_KEY: str = "paraghraps"
PARAGRAPH_DESCRIPTION_FIELD_NAME: str = "content"
PARAGRAPH_DESCRIPTION_EMBEDDING_FIELD_NAME: str = "content_embeddings"
TEXT_EMBEDDING_MODEL: str = "sdadas/st-polish-paraphrase-from-distilroberta"
K_NEAREST_NEIGHBORS_DEFAULT_VALUE: int = 10
VSS_INDEX: str = f"idx:{PARAGRAPH_KEY}_vss"

client = redis.Redis(host="localhost", port=6379, decode_responses=True)
embedder = SentenceTransformer(TEXT_EMBEDDING_MODEL)

def get_paragraphs() -> list[str]:
    # Load articles and paragraphs from their respective JSON files
    with open("articles.json", encoding="utf-8") as articles_file:
        articles = json.load(articles_file)

    with open("paragraphs.json", encoding="utf-8") as paragraphs_file:
        paragraphs = json.load(paragraphs_file)

    # Organize paragraphs by article_id
    paragraphs_by_article = {}
    for paragraph in paragraphs:
        article_id = paragraph["article_id"]
        if article_id not in paragraphs_by_article:
            paragraphs_by_article[article_id] = []
        paragraphs_by_article[article_id].append(paragraph["content"])

    # Combine paragraphs for each article into a single string
    combined_articles = []
    for article in articles:
        article_id = article["id"]
        if article_id in paragraphs_by_article:
            combined_text = " ".join(paragraphs_by_article[article_id])
            combined_articles.append({'content': combined_text})

    return combined_articles


def load_data_to_redis(paragraphs: list[object]):
    pipeline = client.pipeline()
    for i, paraghraph in enumerate(paragraphs, start=1):
        redis_key = f"{PARAGRAPH_KEY}:{i:03}"
        pipeline.json().set(redis_key,"$",paraghraph)
    pipeline.execute()

def create_text_embeddings():
    keys = sorted(client.keys(f"{PARAGRAPH_KEY}:*"))
    descriptions = client.json().mget(keys, f"$.{PARAGRAPH_DESCRIPTION_FIELD_NAME}")
    descriptions = [item for sublist in descriptions for item in sublist]
    embeddings = embedder.encode(descriptions).astype(np.float32).tolist()
    
    pipeline = client.pipeline()
    for key, embedding in zip(keys, embeddings):
        pipeline.json().set(key, f"$.{PARAGRAPH_DESCRIPTION_EMBEDDING_FIELD_NAME}", embedding)
    pipeline.execute()

def prepare_vss_index():
    schema = (
        TagField("$.type", as_name="type"),
        TextField(f"$.{PARAGRAPH_DESCRIPTION_FIELD_NAME}", as_name=PARAGRAPH_DESCRIPTION_FIELD_NAME),
        VectorField(
            f"$.{PARAGRAPH_DESCRIPTION_EMBEDDING_FIELD_NAME}",
            "FLAT",
            {
                "TYPE": "FLOAT32",
                "DIM": 768,
                "DISTANCE_METRIC": "COSINE",
            },
            as_name="vector",
        ),
    )
    definition = IndexDefinition(prefix=[f"{PARAGRAPH_KEY}:"], index_type=IndexType.JSON)
    client.ft(VSS_INDEX).create_index(fields=schema, definition=definition)

def setup():
    load_data_to_redis(get_paragraphs())
    create_text_embeddings()
    prepare_vss_index()

def k_nearest_neighbors(prompt: str, k: int = K_NEAREST_NEIGHBORS_DEFAULT_VALUE) -> list[str]:
    encoded_prompt = embedder.encode(prompt)
    query = (
        Query(f'(*)=>[KNN {k} @vector $query_vector AS vector_score]')
        .sort_by('vector_score')
        .return_fields("id", 'vector_score', PARAGRAPH_DESCRIPTION_FIELD_NAME)
        .dialect(2)
    )
    result_docs = client.ft(VSS_INDEX).search(
        query,
        {
            "query_vector": np.array(encoded_prompt, dtype=np.float32).tobytes()
        }
    ).docs
    vector_score = result_docs[0].vector_score
    print("\n".join([f"kolejny paragraf - {doc.content}" for doc in result_docs]))
    

def main():
    #setup()
    #k_nearest_neighbors("Wróciłem ostatnio z afryki mam wymioty i bóle brzucha, bolą mnie mięsnie")
    k_nearest_neighbors("Mam gorączkę katar kaszel, bolą mnie mięśnie i gardło")

if __name__ == "__main__":
    main()