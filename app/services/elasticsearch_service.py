from elasticsearch import Elasticsearch, exceptions

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")

def create_index(index_name, mappings):
    """
    Create an Elasticsearch index with mappings.
    """
    if es.indices.exists(index=index_name):
        print(f"Index '{index_name}' already exists.")
        return
    es.indices.create(index=index_name, body=mappings)
    print(f"Index '{index_name}' created successfully.")

def index_data(index_name, data):
    """
    Index a document in Elasticsearch with error handling.
    """
    try:
        # Ensure 'customerID' exists in the document
        customer_id = data.get("customerID", "Unknown ID")
        es.index(index=index_name, body=data)
        print(f"Indexed document with customerID: {customer_id}")
    except exceptions.RequestError as e:
        print(f"Error indexing document with customerID {customer_id}: {e.info}")
    except KeyError as e:
        print(f"KeyError indexing document: Missing key {e}")
    except Exception as e:
        print(f"Unexpected error indexing document {customer_id}: {e}")

def search_data(index_name, query):
    """
    Search data in Elasticsearch.
    """
    try:
        response = es.search(index=index_name, body=query)
        return response
    except exceptions.RequestError as e:
        print(f"Search request error: {e.info}")
        return {}
    except Exception as e:
        print(f"Unexpected error during search: {e}")
        return {}
