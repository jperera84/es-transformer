import unittest
from transformer import Transformer, MatchFilter, TermFilter, RangeFilter, BoolFilter, TermsFilter, WildcardFilter, IdsFilter, MatchPhraseFilter, MultiMatchFilter, QueryStringFilter  # Import necessary components
import json

class TestTransformer(unittest.TestCase):

    def prettify_query(self, query):
        """Prettifies a nested dictionary (like an Elasticsearch query) as JSON."""
        return json.dumps(query, indent=2)  # Use json.dumps with indentation

    def test_empty_filters(self):
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": []})
        expected_query = {"query": {}, "size": 20}
        self.assertEqual(query, expected_query)

    def test_single_term_filter(self):
        filters = [{"category": "Electronics"}]
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": filters})
        expected_query = {"query": {"bool": {"must": [{"term": {"category": "Electronics"}}]}}, "size": 20}
        self.assertEqual(query, expected_query)

    def test_range_filter(self):
        filters = [{"price": {"gt": 10, "lt": 100}}]
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": filters})
        expected_query = {"query": {"bool": {"must": [{"range": {"price": {"gt": 10}}}, {"range": {"price": {"lt": 100}}}]}}, "size": 20}
        self.assertEqual(query, expected_query)

    def test_bool_filter_must_not(self):
        filters = [{"product_name": {"must_not": [{"term": "out_of_stock"}]}}]
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": filters})
        expected_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "must_not": [
                                    {"term": {"product_name": "out_of_stock"}}
                                ]
                            }
                        }
                    ]
                }
            },
            "size": 20
        }
        self.assertEqual(query, expected_query)

    def test_bool_filter_should(self):
        filters = [{"product_name": [{"term": "phone"}, {"term": "tablet"}, {"minimum_should_match": 1}]}]
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": filters})
        expected_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {"term": {"product_name": "phone"}},
                                    {"term": {"product_name": "tablet"}}
                                ],
                                "minimum_should_match": 1
                            }
                        }
                    ]
                }
            },
            "size": 20
        }
        self.assertEqual(query, expected_query)

    def test_ids_filter(self):
        filters = [{"ids": {"values": ["AV456", "BV789"]}}]
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": filters})
        expected_query = {'query': {'ids': {'values': ['AV456', 'BV789']}}, 'size': 20}
        self.assertEqual(query, expected_query)

    def test_match_filter(self):
        filters = [{"product_name": {"match": "phone case"}}]
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": filters})
        expected_query = {"query": {"bool": {"must": [{"match": {"product_name": {"query": "phone case"}}}]}}, "size": 20}
        self.assertEqual(query, expected_query)

    def test_multi_match_filter(self):
        filters = [{"product_name": {"multi_match": "phone case"}}]
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": filters})
        expected_query = {"query": {"bool": {"must": [{"multi_match": {"query": "phone case", "fields": ["product_name"]}}]}}, "size": 20}
        self.assertEqual(query, expected_query)

    def test_match_phrase_filter(self):
        filters = [{"product_name": {"match_phrase": "red phone case"}}]
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": filters})
        expected_query = {"query": {"bool": {"must": [{"match_phrase": {"product_name": "red phone case"}}]}}, "size": 20}
        self.assertEqual(query, expected_query)

    def test_query_string_filter(self):
        filters = [
            {
                "product_name": {
                    "query_string": {
                        "query": "phone case (red OR blue)", 
                        "default_field": "product_name",
                        "default_operator": "AND",
                        "fuzziness": "AUTO"
                    }
                }
            }
        ]
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": filters})
        expected_query = {"query": {"bool": {"must": [
            {
                "query_string": {
                    "query": "phone case (red OR blue)",
                    "default_field": "product_name",
                    "default_operator": "AND",
                    "fuzziness": "AUTO"
                }
            }
        ]}}, "size": 20}
        self.assertEqual(query, expected_query)

    def test_query_string_filter_with_escaping(self):
        filters = [
            {
                "product_name": {  # Or whatever field you are using
                    "query_string": {
                        "query": "kimchy\\!",  # Escaped exclamation mark
                        "fields": ["product_name"] # Or any other fields
                    }
                }
            }
        ]
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": filters})
        expected_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "query_string": {
                                "query": "kimchy\\!",
                                "fields": ["product_name"]
                            }
                        }
                    ]
                }
            },
            "size": 20
        }
        self.assertEqual(query, expected_query)

    def test_terms_filter(self):
        filters = [{"tags": ["new", "featured"]}]
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": filters})
        expected_query = {"query": {"bool": {"must": [{"terms": {"tags": ["new", "featured"]}}]}}, "size": 20}
        self.assertEqual(query, expected_query)

    def test_wildcard_filter(self):
        filters = [{"product_name": {"wildcard": "p*one"}}]
        transformer = Transformer("my_index")
        query = transformer.transform({"filters": filters})
        expected_query = {"query": {"bool": {"must": [{"wildcard": {"product_name": "p*one"}}]}}, "size": 20}
        self.assertEqual(query, expected_query)