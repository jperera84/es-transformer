import unittest
from transformer import WildcardFilter  # Assuming WildcardFilter is in transformer/filter.py

class TestWildcardFilter(unittest.TestCase):

    def test_basic_wildcard(self):
        wildcard_filter = WildcardFilter("username", "user*")
        expected_query = {"wildcard": {"username": {"value": "user*"}}}
        self.assertEqual(wildcard_filter.to_elasticsearch(), expected_query)

    def test_wildcard_with_boost(self):
        wildcard_filter = WildcardFilter("filename", "*.log", boost=2.0)
        expected_query = {"wildcard": {"filename": {"value": "*.log", "boost": 2.0}}}
        self.assertEqual(wildcard_filter.to_elasticsearch(), expected_query)

    def test_case_insensitive_wildcard(self):
        wildcard_filter = WildcardFilter("email", "*@example.com", case_insensitive=True)
        expected_query = {"wildcard": {"email": {"value": "*@example.com", "case_insensitive": True}}}
        self.assertEqual(wildcard_filter.to_elasticsearch(), expected_query)

    def test_wildcard_with_rewrite(self):
        wildcard_filter = WildcardFilter("path", "/home/*", rewrite="constant_score")
        expected_query = {"wildcard": {"path": {"value": "/home/*", "rewrite": "constant_score"}}}
        self.assertEqual(wildcard_filter.to_elasticsearch(), expected_query)

    def test_to_json(self):
        wildcard_filter = WildcardFilter("username", "user*", boost=1.5, case_insensitive=True, rewrite="scoring_boolean")
        expected_json = {
            "type": "wildcard",
            "field": "username",
            "value": "user*",
            "boost": 1.5,
            "case_insensitive": True,
            "rewrite": "scoring_boolean"
        }
        self.assertEqual(wildcard_filter.to_json(), expected_json)

if __name__ == "__main__":
    unittest.main()