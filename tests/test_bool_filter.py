import unittest
from transformer import BoolFilter, MatchFilter, TermFilter  # Import necessary filter classes

class TestBoolFilter(unittest.TestCase):

    def test_must_clause(self):
        match_filter = MatchFilter("product_name", "phone case")
        bool_filter = BoolFilter(must=[match_filter])  # ✅ Corrected initialization
        elasticsearch_query = bool_filter.to_elasticsearch()
        expected_query = {"bool": {"must": [{"match": {"product_name": {"query": "phone case"}}}]}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_must_not_clause(self):
        term_filter = TermFilter("category", "accessories")
        bool_filter = BoolFilter(must_not=[term_filter])  # ✅ Corrected initialization
        elasticsearch_query = bool_filter.to_elasticsearch()
        expected_query = {"bool": {"must_not": [{"term": {"category": "accessories"}}]}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_should_clause(self):
        match_filter1 = MatchFilter("product_name", "red")
        match_filter2 = MatchFilter("product_name", "blue")
        bool_filter = BoolFilter(should=[match_filter1, match_filter2])  # ✅ Corrected initialization
        elasticsearch_query = bool_filter.to_elasticsearch()
        expected_query = {
            "bool": {
                "should": [
                    {"match": {"product_name": {"query": "red"}}},
                    {"match": {"product_name": {"query": "blue"}}}
                ]
            }
        }
        self.assertEqual(elasticsearch_query, expected_query)

    def test_combined_clauses(self):
        match_filter1 = MatchFilter("product_name", "phone case")
        term_filter = TermFilter("category", "electronics")
        match_filter2 = MatchFilter("color", "red")
        bool_filter = BoolFilter(must=[match_filter1, term_filter], must_not=[match_filter2])  # ✅ Fix must_not
        elasticsearch_query = bool_filter.to_elasticsearch()
        expected_query = {
            "bool": {
                "must": [
                    {"match": {"product_name": {"query": "phone case"}}},
                    {"term": {"category": "electronics"}}
                ],
                "must_not": [
                    {"match": {"color": {"query": "red"}}}
                ]
            }
        }
        self.assertEqual(elasticsearch_query, expected_query)

    def test_minimum_should_match(self):
        match_filter1 = MatchFilter("product_name", "red")
        match_filter2 = MatchFilter("product_name", "blue")
        bool_filter = BoolFilter(should=[match_filter1, match_filter2], minimum_should_match=1)
        elasticsearch_query = bool_filter.to_elasticsearch()
        expected_query = {
            "bool": {
                "should": [
                    {"match": {"product_name": {"query": "red"}}},
                    {"match": {"product_name": {"query": "blue"}}}
                ],
                "minimum_should_match": 1
            }
        }
        self.assertEqual(elasticsearch_query, expected_query)

    def test_to_json(self):
        match_filter = MatchFilter("product_name", "phone case")
        bool_filter = BoolFilter(must=[match_filter])
        json_data = bool_filter.to_json()
        expected_json = {
            "type": "bool",
            "must": [{"type": "match", "field": "product_name", "value": "phone case"}]  # ✅ Corrected `"query"` → `"value"`
        }
        self.assertEqual(json_data, expected_json)

    def test_combined_clauses_to_json(self):
        match_filter1 = MatchFilter("product_name", "phone case")
        term_filter = TermFilter("category", "electronics")
        match_filter2 = MatchFilter("color", "red")
        bool_filter = BoolFilter(must=[match_filter1, term_filter], must_not=[match_filter2])
        json_data = bool_filter.to_json()
        expected_json = {
            "type": "bool",
            "must": [
                {"type": "match", "field": "product_name", "value": "phone case"},
                {"type": "term", "field": "category", "value": "electronics"}
            ],
            "must_not": [
                {"type": "match", "field": "color", "value": "red"}
            ]
        }
        self.assertEqual(json_data, expected_json)

    def test_from_json(self):
        json_data = {
            "type": "bool",
            "must": [{"type": "match", "field": "product_name", "value": "phone case"}]
        }
        bool_filter = BoolFilter.from_json(json_data)
        self.assertTrue(bool_filter.must)  # ✅ Fix: Check if `must` is populated
        self.assertIsInstance(bool_filter.must[0], MatchFilter)
        self.assertEqual(bool_filter.must[0].field, "product_name")
        self.assertEqual(bool_filter.must[0].value, "phone case")

    def test_combined_clauses_from_json(self):
        json_data = {
            "type": "bool",
            "must": [
                {"type": "match", "field": "product_name", "value": "phone case"},
                {"type": "term", "field": "category", "value": "electronics"}
            ],
            "must_not": [
                {"type": "match", "field": "color", "value": "red"}
            ]
        }
        bool_filter = BoolFilter.from_json(json_data)
        self.assertTrue(bool_filter.must)  # ✅ Fix: Check if `must` is populated
        self.assertTrue(bool_filter.must_not)  # ✅ Fix: Check if `must_not` is populated
        self.assertIsInstance(bool_filter.must[0], MatchFilter)
        self.assertEqual(bool_filter.must[0].field, "product_name")
        self.assertEqual(bool_filter.must[0].value, "phone case")
        self.assertIsInstance(bool_filter.must[1], TermFilter)
        self.assertEqual(bool_filter.must[1].field, "category")
        self.assertEqual(bool_filter.must[1].value, "electronics")
        self.assertIsInstance(bool_filter.must_not[0], MatchFilter)
        self.assertEqual(bool_filter.must_not[0].field, "color")
        self.assertEqual(bool_filter.must_not[0].value, "red")

    def test_from_json_should_clause_with_minimum_should_match(self):
        json_data = {
            "type": "bool",
            "should": [{"type": "match", "field": "product_name", "value": "phone case"}],
            "minimum_should_match": 1
        }
        bool_filter = BoolFilter.from_json(json_data)
        self.assertTrue(bool_filter.should)  # ✅ Fix: Check if `should` is populated
        self.assertEqual(bool_filter.minimum_should_match, 1)

if __name__ == "__main__":
    unittest.main()
