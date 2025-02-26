from elasticsearch import Elasticsearch

from elasticsearch import Elasticsearch

class QueryExecutor:
    def __init__(self, index_name="my-events", es_host="http://localhost:9200", username="elastic", password="5ZdBs31Y"):
        """Initialize Elasticsearch connection with authentication."""
        self.es = Elasticsearch(
            hosts=[es_host],
            basic_auth=(username, password)  # ✅ Pass credentials
        )
        self.index = index_name

    def execute_query(self, query):
        """Executes a search query against Elasticsearch."""
        response = self.es.search(index=self.index, body=query)  # ✅ Remove size from parameters
        return response

# Usage Example:
query_executor = QueryExecutor(username="elastic", password="yourpassword")

