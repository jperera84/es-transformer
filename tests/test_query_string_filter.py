import unittest
from transformer import QueryStringFilter  # Assuming QueryStringFilter is in transformer/filter.py

class TestQueryStringFilter(unittest.TestCase):

    def test_basic_query_string(self):
        query_string_filter = QueryStringFilter("phone case")
        elasticsearch_query = query_string_filter.to_elasticsearch()
        expected_query = {"query_string": {"query": "phone case"}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_query_string_with_default_field(self):
        query_string_filter = QueryStringFilter("phone", default_field="product_name")
        elasticsearch_query = query_string_filter.to_elasticsearch()
        expected_query = {"query_string": {"query": "phone", "default_field": "product_name"}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_query_string_with_analyzer(self):
        query_string_filter = QueryStringFilter("phone case", analyzer="standard")
        elasticsearch_query = query_string_filter.to_elasticsearch()
        expected_query = {"query_string": {"query": "phone case", "analyzer": "standard"}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_query_string_with_boost(self):
        query_string_filter = QueryStringFilter("phone case", boost=2.0)
        elasticsearch_query = query_string_filter.to_elasticsearch()
        expected_query = {"query_string": {"query": "phone case", "boost": 2.0}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_query_string_with_default_operator(self):
        query_string_filter = QueryStringFilter("phone case", default_operator="AND")
        elasticsearch_query = query_string_filter.to_elasticsearch()
        expected_query = {"query_string": {"query": "phone case", "default_operator": "AND"}}
        self.assertEqual(elasticsearch_query, expected_query)

    # ... (Add tests for other parameters: allow_leading_wildcard, lowercase_expanded_terms, etc.)

    def test_to_json(self):
        query_string_filter = QueryStringFilter("phone case", default_field="product_name", analyzer="standard", boost=2.0, default_operator="AND")
        json_data = query_string_filter.to_json()
        expected_json = {"type": "query_string", "query": "phone case", "default_field": "product_name", "analyzer": "standard", "boost": 2.0, "default_operator": "AND"}
        self.assertEqual(json_data, expected_json)

    def test_from_json(self):
        json_data = {"type": "query_string", "query": "phone case", "default_field": "product_name", "analyzer": "standard", "boost": 2.0, "default_operator": "AND"}
        query_string_filter = QueryStringFilter.from_json(json_data)
        self.assertEqual(query_string_filter.query, "phone case")
        self.assertEqual(query_string_filter.default_field, "product_name")
        self.assertEqual(query_string_filter.analyzer, "standard")
        self.assertEqual(query_string_filter.boost, 2.0)
        self.assertEqual(query_string_filter.default_operator, "AND")

    def test_from_json_without_optional_params(self):
        json_data = {"type": "query_string", "query": "phone case"}
        query_string_filter = QueryStringFilter.from_json(json_data)
        self.assertEqual(query_string_filter.query, "phone case")
        self.assertIsNone(query_string_filter.default_field)
        self.assertIsNone(query_string_filter.analyzer)
        self.assertIsNone(query_string_filter.boost)
        self.assertIsNone(query_string_filter.default_operator)

if __name__ == "__main__":
    unittest.main()