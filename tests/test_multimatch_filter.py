import unittest
from transformer import MultiMatchFilter  # Assuming MultiMatchFilter is in transformer/filter.py

class TestMultiMatchFilter(unittest.TestCase):

    def test_basic_multi_match(self):
        multi_match_filter = MultiMatchFilter("phone case", ["product_name", "description"])
        elasticsearch_query = multi_match_filter.to_elasticsearch()
        expected_query = {"multi_match": {"query": "phone case", "fields": ["product_name", "description"]}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_multi_match_with_type(self):
        multi_match_filter = MultiMatchFilter("phone case", ["product_name", "description"], type="best_fields")
        elasticsearch_query = multi_match_filter.to_elasticsearch()
        expected_query = {"multi_match": {"query": "phone case", "fields": ["product_name", "description"], "type": "best_fields"}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_multi_match_with_boost(self):
        multi_match_filter = MultiMatchFilter("phone case", ["product_name", "description"], boost=2.0)
        elasticsearch_query = multi_match_filter.to_elasticsearch()
        expected_query = {"multi_match": {"query": "phone case", "fields": ["product_name", "description"], "boost": 2.0}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_multi_match_with_fuzziness(self):
        multi_match_filter = MultiMatchFilter("phone case", ["product_name", "description"], fuzziness="AUTO")
        elasticsearch_query = multi_match_filter.to_elasticsearch()
        expected_query = {"multi_match": {"query": "phone case", "fields": ["product_name", "description"], "fuzziness": "AUTO"}}
        self.assertEqual(elasticsearch_query, expected_query)

    # ... (Add tests for other parameters: operator, cutoff_frequency, etc.)

    def test_to_json(self):
        multi_match_filter = MultiMatchFilter("phone case", ["product_name", "description"], type="best_fields", boost=2.0, fuzziness="AUTO")
        json_data = multi_match_filter.to_json()
        expected_json = {"type": "multi_match", "query": "phone case", "fields": ["product_name", "description"], "type_name": "best_fields", "boost": 2.0, "fuzziness": "AUTO"}
        self.assertEqual(json_data, expected_json)

    def test_from_json(self):
        json_data = {"type": "multi_match", "query": "phone case", "fields": ["product_name", "description"], "type_name": "best_fields", "boost": 2.0, "fuzziness": "AUTO"}
        multi_match_filter = MultiMatchFilter.from_json(json_data)
        self.assertEqual(multi_match_filter.query, "phone case")
        self.assertEqual(multi_match_filter.fields, ["product_name", "description"])
        self.assertEqual(multi_match_filter.type, "best_fields")
        self.assertEqual(multi_match_filter.boost, 2.0)
        self.assertEqual(multi_match_filter.fuzziness, "AUTO")

    # ... (Add from_json tests for other parameters)

if __name__ == "__main__":
    unittest.main()