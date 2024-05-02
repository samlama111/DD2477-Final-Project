import os
from elasticsearch import Elasticsearch

CLOUD_ID = os.getenv("CLOUD_ID")
API_KEY = os.getenv("API_KEY")
print(CLOUD_ID)

# Setup Elasticsearch connection
es = Elasticsearch(cloud_id=CLOUD_ID, api_key=API_KEY)


def check_connection():
    if es.ping():
        print("Connected to Elasticsearch!")
    else:
        print("Could not connect to Elasticsearch.")


def create_index(index_name, mapping):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=mapping)
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Index '{index_name}' already exists.")


def delete_index(index_name):
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Index '{index_name}' deleted successfully.")
    else:
        print(f"Index '{index_name}' does not exist.")
