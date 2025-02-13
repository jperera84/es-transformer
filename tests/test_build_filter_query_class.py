import unittest
from transformer import build_filter_query_class, create_filter_object, MatchFilter, TermFilter, RangeFilter, BoolFilter, TermsFilter, WildcardFilter, IdsFilter, MatchPhraseFilter, MultiMatchFilter, QueryStringFilter  # Import necessary components

class TestBuildFilterQueryClass(unittest.TestCase):

    def test_build_filter_query_class_combined_clauses(self):
        filter_data = [
            [{"price": {"gt": 10, "lt": 100}}],
            [{"category": "Electronics"}],
            [{"tags": ["new", "featured"]}],
            [{"date_added": {"gte": "2024-01-01", "lte": "2024-01-31"}}],
            [
                {"product_name": [
                    {"term": "phone"},
                    {"term": "tablet"},
                    {"term": "laptop"},
                    {"wildcard": "p*one"},
                    {"minimum_should_match": 2}
                ]}
            ],
            [
                {"product_name": {
                    "must_not": [
                        {"term": "out_of_stock"},
                        {"term": "discontinued"}
                    ]
                }}
            ],
            [
                {"brand": "Samsung"},
                {
                    "color": [
                        {"term": "black"},
                        {"term": "white"},
                        {"minimum_should_match": 1}
                    ]
                }
            ],
            [{"product_name": {"match": {"query": "phone case", "fuzziness": "AUTO"}}}],
            [{"ids": {"values": ["AV456", "BV789", "CV012"]}}],
            [
                {"product_name": {
                    "multi_match": {
                        "query": "phone case",
                        "fields": ["product_name", "description"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                }}
            ],
            [
                {"product_name": {
                    "multi_match": "phone case"
                }}
            ],
            [{"product_name": {"match_phrase": {"query": "red phone case", "slop": 2}}}],
            [
                {"product_name": {
                    "query_string": {
                        "query": "phone case (red OR blue)",
                        "default_field": "product_name",
                        "default_operator": "AND",
                        "fuzziness": "AUTO"
                    }
                }}
            ],
        ]

        query = build_filter_query_class(filter_data)

        expected_query = {
            "bool": {
                "must": [
                    {"range": {"price": {"gt": 10}}},
                    {"range": {"price": {"lt": 100}}},
                    {"term": {"category": "Electronics"}},
                    {"terms": {"tags": ["new", "featured"]}},
                    {"range": {"date_added": {"gte": "2024-01-01"}}},
                    {"range": {"date_added": {"lte": "2024-01-31"}}},
                    {"bool": {"should": [{"term": {"product_name": "phone"}}, {"term": {"product_name": "tablet"}}, {"term": {"product_name": "laptop"}}, {"wildcard": {"product_name": "p*one"}}], "minimum_should_match": 2}},
                    {"bool": {"must_not": [{"term": {"product_name": "out_of_stock"}}, {"term": {"product_name": "discontinued"}}]}},
                    {"term": {"brand": "Samsung"}},
                    {"bool": {"should": [{"term": {"color": "black"}}, {"term": {"color": "white"}}], "minimum_should_match": 1}},
                    {"match": {"product_name": {"query": "phone case", "fuzziness": "AUTO"}}},
                    {"ids": {"values": ["AV456", "BV789", "CV012"]}},
                    {"multi_match": {"query": "phone case", "fields": ["product_name", "description"], "type": "best_fields", "fuzziness": "AUTO"}},
                    {"multi_match": {"query": "phone case", "fields": ["product_name"]}}, # Corrected simple multi_match
                    {"match_phrase": {"product_name": {"query": "red phone case", "slop": 2}}}, # Added missing "query" key
                    {"query_string": {"query": "phone case (red OR blue)", "default_field": "product_name", "default_operator": "AND", "fuzziness": "AUTO"}}
                ]
            }
        }

        self.assertEqual(query, expected_query)

    # ... (Add other test cases as needed)

    def test_build_filter_query_class_empty(self):
        filter_data = []  # Empty filter data
        query = build_filter_query_class(filter_data)
        self.assertEqual(query, {})  # Expect an empty dictionary

    def test_build_filter_query_class_simple_match(self):
        filter_data = [[{"product_name": {"match": "phone case"}}]]
        query = build_filter_query_class(filter_data)
        expected_query = {"bool": {"must": [{"match": {"product_name": {"query": "phone case"}}}]}}
        self.assertEqual(query, expected_query )

    def test_build_filter_query_class_simple_term(self):
        filter_data = [[{"category": "Electronics"}]]
        query = build_filter_query_class(filter_data)
        expected_query = {"bool": {"must": [{"term": {"category": "Electronics"}}]}}
        self.assertEqual(query, expected_query)

    def test_build_filter_query_class_terms(self):
        filter_data = [[{"tags": ["new", "featured"]}]]
        query = build_filter_query_class(filter_data)
        expected_query = {"bool": {"must": [{"terms": {"tags": ["new", "featured"]}}]}}
        self.assertEqual(query, expected_query)

    def test_build_filter_query_class_wildcard(self):
        filter_data = [[{"product_name": {"wildcard": "p*one"}}]]
        query = build_filter_query_class(filter_data)
        expected_query = {"bool": {"must": [{"wildcard": {"product_name": "p*one"}}]}}
        self.assertEqual(query, expected_query)

    def test_build_filter_query_class_ids(self):
        filter_data = [[{"ids": {"values": ["AV456", "BV789", "CV012"]}}]]
        query = build_filter_query_class(filter_data)
        expected_query = {"bool": {"must": [{"ids": {"values": ["AV456", "BV789", "CV012"]}}]}}
        self.assertEqual(query, expected_query)

    def test_build_filter_query_class_match_phrase(self):
        filter_data = [[{"product_name": {"match_phrase": "red phone case"}}]]
        query = build_filter_query_class(filter_data)
        expected_query = {"bool": {"must": [{"match_phrase": {"product_name": {"query": "red phone case"}}}]}}
        self.assertEqual(query, expected_query)

    def test_build_filter_query_class_multi_match(self):
        filter_data = [[{"product_name": {"multi_match": "phone case"}}]]
        query = build_filter_query_class(filter_data)
        expected_query = {"bool": {"must": [{"multi_match": {"query": "phone case", "fields": ["product_name"]}}]}}
        self.assertEqual(query, expected_query)

    def test_build_filter_query_class_query_string(self):
        filter_data = [[{"product_name": {"query_string": "phone case"}}]]
        query = build_filter_query_class(filter_data)
        expected_query = {"bool": {"must": [{"query_string": {"query": "phone case"}}]}}
        self.assertEqual(query, expected_query)