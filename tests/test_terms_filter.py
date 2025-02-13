import unittest
from transformer import TermsFilter  # Assuming TermsFilter is in transformer/filter.py

class TestTermsFilter(unittest.TestCase):

    def test_single_term(self):
        terms_filter = TermsFilter("category", "electronics")
        elasticsearch_query = terms_filter.to_elasticsearch()
        expected_query = {"terms": {"category": ["electronics"]}}  # Terms expects a list
        self.assertEqual(elasticsearch_query, expected_query)

    def test_multiple_terms(self):
        terms_filter = TermsFilter("category", ["electronics", "books", "clothing"])
        elasticsearch_query = terms_filter.to_elasticsearch()
        expected_query = {"terms": {"category": ["electronics", "books", "clothing"]}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_empty_terms_list(self):
        terms_filter = TermsFilter("category", [])  # Empty list of terms
        elasticsearch_query = terms_filter.to_elasticsearch()
        expected_query = {"terms": {"category": []}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_numeric_terms(self):
      terms_filter = TermsFilter("product_id", [123, 456, 789])
      elasticsearch_query = terms_filter.to_elasticsearch()
      expected_query = {"terms": {"product_id": [123, 456, 789]}}
      self.assertEqual(elasticsearch_query, expected_query)

    def test_to_json_single_term(self):
        terms_filter = TermsFilter("category", "electronics")
        json_data = terms_filter.to_json()
        expected_json = {"type": "terms", "field": "category", "terms": ["electronics"]}
        self.assertEqual(json_data, expected_json)

    def test_to_json_multiple_terms(self):
        terms_filter = TermsFilter("category", ["electronics", "books"])
        json_data = terms_filter.to_json()
        expected_json = {"type": "terms", "field": "category", "terms": ["electronics", "books"]}
        self.assertEqual(json_data, expected_json)

    def test_from_json_single_term(self):
        json_data = {"type": "terms", "field": "category", "terms": ["electronics"]}
        terms_filter = TermsFilter.from_json(json_data)
        self.assertEqual(terms_filter.field, "category")
        self.assertEqual(terms_filter.terms, ["electronics"])

    def test_from_json_multiple_terms(self):
        json_data = {"type": "terms", "field": "category", "terms": ["electronics", "books"]}
        terms_filter = TermsFilter.from_json(json_data)
        self.assertEqual(terms_filter.field, "category")
        self.assertEqual(terms_filter.terms, ["electronics", "books"])

if __name__ == "__main__":
    unittest.main()