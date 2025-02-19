import unittest
from transformer.filter import TermsFilter

class TestTermsFilter(unittest.TestCase):

    def test_single_term(self):
        terms_filter = TermsFilter("category", "electronics")
        expected_query = {"terms": {"category": ["electronics"]}}  # Terms expects a list
        self.assertEqual(terms_filter.to_elasticsearch(), expected_query)

    def test_multiple_terms(self):
        terms_filter = TermsFilter("category", ["electronics", "books", "clothing"])
        expected_query = {"terms": {"category": ["electronics", "books", "clothing"]}}
        self.assertEqual(terms_filter.to_elasticsearch(), expected_query)

    def test_empty_terms_list(self):
        terms_filter = TermsFilter("category", [])  # Empty list of terms
        expected_query = {"terms": {"category": []}}
        self.assertEqual(terms_filter.to_elasticsearch(), expected_query)

    def test_numeric_terms(self):
        terms_filter = TermsFilter("product_id", [123, 456, 789])
        expected_query = {"terms": {"product_id": [123, 456, 789]}}
        self.assertEqual(terms_filter.to_elasticsearch(), expected_query)

    def test_terms_with_boost(self):
        terms_filter = TermsFilter("tags", ["new", "featured"], boost=1.5)
        expected_query = {"terms": {"tags": ["new", "featured"], "boost": 1.5}}
        self.assertEqual(terms_filter.to_elasticsearch(), expected_query)

    def test_to_json_single_term(self):
        terms_filter = TermsFilter("category", "electronics")
        expected_json = {"type": "terms", "field": "category", "terms": ["electronics"]}
        self.assertEqual(terms_filter.to_json(), expected_json)

    def test_to_json_multiple_terms(self):
        terms_filter = TermsFilter("category", ["electronics", "books"])
        expected_json = {"type": "terms", "field": "category", "terms": ["electronics", "books"]}
        self.assertEqual(terms_filter.to_json(), expected_json)

    def test_to_json_with_boost(self):
        terms_filter = TermsFilter("tags", ["new", "featured"], boost=1.5)
        expected_json = {
            "type": "terms",
            "field": "tags",
            "terms": ["new", "featured"],
            "boost": 1.5
        }
        self.assertEqual(terms_filter.to_json(), expected_json)

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

    def test_from_json_with_boost(self):
        json_data = {"type": "terms", "field": "tags", "terms": ["new", "featured"], "boost": 1.5}
        terms_filter = TermsFilter.from_json(json_data)
        self.assertEqual(terms_filter.field, "tags")
        self.assertEqual(terms_filter.terms, ["new", "featured"])
        self.assertEqual(terms_filter.boost, 1.5)

if __name__ == "__main__":
    unittest.main()
