import unittest
from transformer import BoolFilter, MatchFilter, TermFilter  # Import necessary filter classes

class TestBoolFilter(unittest.TestCase):

    def test_must_clause(self):
        match_filter = MatchFilter("product_name", "phone case")
        bool_filter = BoolFilter("must", [match_filter])
        elasticsearch_query = bool_filter.to_elasticsearch()
        expected_query = {"bool": {"must": [{"match": {"product_name": {"query": "phone case"}}}]}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_must_not_clause(self):
        term_filter = TermFilter("category", "accessories")
        bool_filter = BoolFilter("must_not", [term_filter])
        elasticsearch_query = bool_filter.to_elasticsearch()
        expected_query = {"bool": {"must_not": [{"term": {"category": "accessories"}}]}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_should_clause(self):
        match_filter1 = MatchFilter("product_name", "red")
        match_filter2 = MatchFilter("product_name", "blue")
        bool_filter = BoolFilter("should", [match_filter1, match_filter2])
        elasticsearch_query = bool_filter.to_elasticsearch()
        expected_query = {"bool": {"should": [{"match": {"product_name": {"query": "red"}}}, {"match": {"product_name": {"query": "blue"}}}]}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_combined_clauses(self):
        match_filter1 = MatchFilter("product_name", "phone case")
        term_filter = TermFilter("category", "electronics")
        match_filter2 = MatchFilter("color", "red")
        bool_filter = BoolFilter("must", [match_filter1, term_filter])
        bool_filter.must_not = [match_filter2]  # Add a must_not clause
        elasticsearch_query = bool_filter.to_elasticsearch()
        expected_query = {"bool": {"must": [{"match": {"product_name": {"query": "phone case"}}}, {"term": {"category": "electronics"}}], "must_not": [{"match": {"color": {"query": "red"}}}]}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_minimum_should_match(self):
        match_filter1 = MatchFilter("product_name", "red")
        match_filter2 = MatchFilter("product_name", "blue")
        bool_filter = BoolFilter("should", [match_filter1, match_filter2], minimum_should_match=1)
        elasticsearch_query = bool_filter.to_elasticsearch()
        expected_query = {"bool": {"should": [{"match": {"product_name": {"query": "red"}}}, {"match": {"product_name": {"query": "blue"}}}], "minimum_should_match": 1}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_to_json(self):
        match_filter = MatchFilter("product_name", "phone case")
        bool_filter = BoolFilter("must", [match_filter])
        json_data = bool_filter.to_json()
        expected_json = {"type": "bool", "must": [{"type": "match", "field": "product_name", "query": "phone case"}]}
        self.assertEqual(json_data, expected_json)

    def test_combined_clauses_to_json(self):
        match_filter1 = MatchFilter("product_name", "phone case")
        term_filter = TermFilter("category", "electronics")
        match_filter2 = MatchFilter("color", "red")
        bool_filter = BoolFilter("must", [match_filter1, term_filter])
        bool_filter.must_not = [match_filter2]
        json_data = bool_filter.to_json()
        expected_json = {"type": "bool", "must": [{"type": "match", "field": "product_name", "query": "phone case"}, {"type": "term", "field": "category", "value": "electronics"}], "must_not": [{"type": "match", "field": "color", "query": "red"}]}
        self.assertEqual(json_data, expected_json)

    def test_from_json(self):
        json_data = {"type": "bool", "must": [{"type": "match", "field": "product_name", "query": "phone case"}]}
        bool_filter = BoolFilter.from_json(json_data)
        self.assertEqual(bool_filter.clause, "must")
        self.assertEqual(len(bool_filter.filters), 1)
        self.assertIsInstance(bool_filter.filters[0], MatchFilter)
        self.assertEqual(bool_filter.filters[0].field, "product_name")
        self.assertEqual(bool_filter.filters[0].query, "phone case")

    def test_combined_clauses_from_json(self):
        json_data = {"type": "bool", "must": [{"type": "match", "field": "product_name", "query": "phone case"}, {"type": "term", "field": "category", "value": "electronics"}], "must_not": [{"type": "match", "field": "color", "query": "red"}]}
        bool_filter = BoolFilter.from_json(json_data)
        self.assertEqual(bool_filter.clause, "must")
        self.assertEqual(len(bool_filter.filters), 2)
        self.assertIsInstance(bool_filter.filters[0], MatchFilter)
        self.assertEqual(bool_filter.filters[0].field, "product_name")
        self.assertEqual(bool_filter.filters[0].query, "phone case")
        self.assertIsInstance(bool_filter.filters[1], TermFilter)
        self.assertEqual(bool_filter.filters[1].field, "category")
        self.assertEqual(bool_filter.filters[1].value, "electronics")
        self.assertEqual(len(bool_filter.must_not), 1)
        self.assertIsInstance(bool_filter.must_not[0], MatchFilter)
        self.assertEqual(bool_filter.must_not[0].field, "color")
        self.assertEqual(bool_filter.must_not[0].query, "red")

    def test_from_json_should_clause_with_minimum_should_match(self):
        json_data = {"type": "bool", "should": [{"type": "match", "field": "product_name", "query": "phone case"}], "minimum_should_match": 1}
        bool_filter = BoolFilter.from_json(json_data)
        self.assertEqual(bool_filter.clause, "should")
        self.assertEqual(bool_filter.minimum_should_match, 1)

if __name__ == "__main__":
    unittest.main()
