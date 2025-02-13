import unittest
from transformer import WildcardFilter  # Assuming WildcardFilter is in transformer/filter.py

class TestWildcardFilter(unittest.TestCase):

    def test_basic_wildcard(self):
        wildcard_filter = WildcardFilter("product_name", "p*one")
        elasticsearch_query = wildcard_filter.to_elasticsearch()
        expected_query = {"wildcard": {"product_name": "p*one"}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_wildcard_with_question_mark(self):
        wildcard_filter = WildcardFilter("product_name", "ph?ne")
        elasticsearch_query = wildcard_filter.to_elasticsearch()
        expected_query = {"wildcard": {"product_name": "ph?ne"}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_wildcard_with_escaped_characters(self):
        wildcard_filter = WildcardFilter("file_path", "C:\\\\Users\\\\*") # Escaping backslashes
        elasticsearch_query = wildcard_filter.to_elasticsearch()
        expected_query = {"wildcard": {"file_path": "C:\\\\Users\\\\*"}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_wildcard_with_boost(self):
        wildcard_filter = WildcardFilter("product_name", "p*one", boost=2.0)
        elasticsearch_query = wildcard_filter.to_elasticsearch()
        expected_query = {"wildcard": {"product_name": {"value": "p*one", "boost": 2.0}}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_to_json(self):
        wildcard_filter = WildcardFilter("product_name", "p*one", boost=2.0)
        json_data = wildcard_filter.to_json()
        expected_json = {"type": "wildcard", "field": "product_name", "value": "p*one", "boost": 2.0}
        self.assertEqual(json_data, expected_json)

    def test_from_json(self):
        json_data = {"type": "wildcard", "field": "product_name", "value": "p*one", "boost": 2.0}
        wildcard_filter = WildcardFilter.from_json(json_data)
        self.assertEqual(wildcard_filter.field, "product_name")
        self.assertEqual(wildcard_filter.value, "p*one")
        self.assertEqual(wildcard_filter.boost, 2.0)

    def test_from_json_without_boost(self):
        json_data = {"type": "wildcard", "field": "product_name", "value": "p*one"}
        wildcard_filter = WildcardFilter.from_json(json_data)
        self.assertEqual(wildcard_filter.field, "product_name")
        self.assertEqual(wildcard_filter.value, "p*one")
        self.assertIsNone(wildcard_filter.boost)

if __name__ == "__main__":
    unittest.main()