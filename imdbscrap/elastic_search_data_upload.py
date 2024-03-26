import os
import uuid
import json
from elasticsearch import Elasticsearch

# Configure in system API host, username and password
# Retreive system data
ELASTIC_API_URL_HOST = os.environ['ELASTIC_API_URL_HOST']
ELASTIC_API_USERNAME = os.environ['ELASTIC_API_USERNAME']
ELASTIC_API_PASSWORD = os.environ['ELASTIC_API_PASSWORD']

# Create elastic connection
es=Elasticsearch(
    [ELASTIC_API_URL_HOST], 
    http_auth=(ELASTIC_API_USERNAME, ELASTIC_API_PASSWORD))


# Read from imdb JSON file
with open('./imdbscrap/spiders/imdb.json', 'r') as f:
    data = json.load(f)

# Iterate over each object in the JSON data
for obj in data:
    # Generate a unique ID for the document
    doc_id = uuid.uuid4()

    # Upload document
    es.index(
        index='imdb',
        id=doc_id,
        document=obj
    )
