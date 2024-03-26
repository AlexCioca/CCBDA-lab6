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

# Delete all documents using the Delete by Query API with a match_all query
try:
  response = es.delete_by_query(index='imdb', body={"query": {"match_all": {}}})
  print(f"Deleted {response['deleted']:,} documents from index imdb.")
except Exception as e:
  print(f"Error deleting documents: {e}")


# Read from imdb JSON file
with open('./imdbscrap/spiders/data.json', 'r') as f:
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
