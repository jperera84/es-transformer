import unittest
from transformer import TermFilter

class TestTermFilter(unittest.TestCase):

    def test_basic_term_filter(self):
        term_filter = TermFilter("category", "electronics")
        elasticsearch_query = term_filter.to_elasticsearch()
        expected_query = {"term": {"category": "electronics"}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_term_filter_with_boost(self):
        term_filter = TermFilter("category", "electronics", boost=2.0)
        elasticsearch_query = term_filter.to_elasticsearch()
        expected_query = {"term": {"category": {"value": "electronics", "boost": 2.0}}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_term_filter_with_case_insensitivity(self):  # Example - depends on your mapping
        term_filter = TermFilter("category", "Electronics")  # Note the capitalization
        elasticsearch_query = term_filter.to_elasticsearch()
        expected_query = {"term": {"category": "Electronics"}} # Case sensitive by default
        self.assertEqual(elasticsearch_query, expected_query)

    def test_term_filter_with_numeric_value(self):
        term_filter = TermFilter("product_id", 123)  # Numeric value
        elasticsearch_query = term_filter.to_elasticsearch()
        expected_query = {"term": {"product_id": 123}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_term_filter_with_zero(self):
        term_filter = TermFilter("product_id", 0)  # Numeric value
        elasticsearch_query = term_filter.to_elasticsearch()
        expected_query = {"term": {"product_id": 0}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_term_filter_with_boolean(self):
        term_filter = TermFilter("is_featured", True)  # Boolean value
        elasticsearch_query = term_filter.to_elasticsearch()
        expected_query = {"term": {"is_featured": True}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_term_filter_with_none(self):
        term_filter = TermFilter("category", None)  # None value
        elasticsearch_query = term_filter.to_elasticsearch()
        expected_query = {"term": {"category": None}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_term_filter_with_to_json(self):
        term_filter = TermFilter("category", "electronics", boost=2.0)
        json_data = term_filter.to_json()
        expected_json = {"type": "term", "field": "category", "value": "electronics", "boost": 2.0}
        self.assertEqual(json_data, expected_json)

    def test_term_filter_from_json(self):
      json_data = {"type": "term", "field": "category", "value": "electronics", "boost": 2.0}
      term_filter = TermFilter.from_json(json_data)
      self.assertEqual(term_filter.field, "category")
      self.assertEqual(term_filter.value, "electronics")
      self.assertEqual(term_filter.boost, 2.0)

    def test_term_filter_from_json_without_boost(self):
      json_data = {"type": "term", "field": "category", "value": "electronics"}
      term_filter = TermFilter.from_json(json_data)
      self.assertEqual(term_filter.field, "category")
      self.assertEqual(term_filter.value, "electronics")
      self.assertIsNone(term_filter.boost)  # Check that boost is None if not provided

if __name__ == "__main__":
    unittest.main()