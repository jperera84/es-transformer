import unittest
from transformer import WildcardFilter  # Assuming WildcardFilter is in transformer/filter.py

class TestWildcardFilter(unittest.TestCase):

    def test_wildcard_basic(self):
        wildcard_filter = WildcardFilter("filename", "*.log")
        elasticsearch_query = wildcard_filter.to_elasticsearch()
        expected_query = {
            "wildcard": {
                "filename": {
                    "value": "*.log"
                }
            }
        }
        self.assertEqual(elasticsearch_query, expected_query)

    def test_wildcard_with_boost(self):
        """✅ FIX: Boost should be applied inside a `bool.should` query"""
        wildcard_filter = WildcardFilter("filename", "*.log", boost=2.0)
        elasticsearch_query = wildcard_filter.to_elasticsearch()
        expected_query = {
            "bool": {
                "should": [
                    {
                        "wildcard": {
                            "filename": {
                                "value": "*.log"
                            }
                        }
                    }
                ],
                "minimum_should_match": 1,
                "boost": 2.0
            }
        }
        self.assertEqual(elasticsearch_query, expected_query)


    def test_case_insensitive_wildcard(self):
        wildcard_filter = WildcardFilter("email", "*@example.com", case_insensitive=True)
        expected_query = {
            "wildcard": {
                "email": {
                    "value": "*@example.com",
                    "case_insensitive": True
                }
            }
        }
        self.assertEqual(wildcard_filter.to_elasticsearch(), expected_query)

    def test_wildcard_with_rewrite(self):
        wildcard_filter = WildcardFilter("path", "/home/*", rewrite="constant_score")
        expected_query = {
            "wildcard": {
                "path": {
                    "value": "/home/*",
                    "rewrite": "constant_score"
                }
            }
        }
        self.assertEqual(wildcard_filter.to_elasticsearch(), expected_query)

    def test_to_json(self):
        wildcard_filter = WildcardFilter("username", "user*", boost=1.5, case_insensitive=True, rewrite="scoring_boolean")
        json_data = wildcard_filter.to_json()
        expected_json = {
            "type": "wildcard",
            "field": "username",
            "value": "user*",
            "boost": 1.5,
            "case_insensitive": True,
            "rewrite": "scoring_boolean"
        }
        self.assertEqual(json_data, expected_json)

if __name__ == "__main__":
    unittest.main()
