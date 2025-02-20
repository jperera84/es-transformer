import unittest
from transformer import MatchFilter  # Assuming MatchFilter is in transformer/filter.py

class TestMatchFilter(unittest.TestCase):

    QUICK_BROWN_FOX = "quick brown fox"

    def test_basic_match(self):
        match_filter = MatchFilter("title", self.QUICK_BROWN_FOX)
        elasticsearch_query = match_filter.to_elasticsearch()
        expected_query = {
            "match": {
                "title": {
                    "query": self.QUICK_BROWN_FOX
                }
            }
        }
        self.assertEqual(elasticsearch_query, expected_query)

    def test_match_with_analyzer(self):
        """✅ FIX: Ensure `analyzer` is included in the match query"""
        match_filter = MatchFilter("title", self.QUICK_BROWN_FOX, analyzer="standard")
        elasticsearch_query = match_filter.to_elasticsearch()
        expected_query = {
            "match": {
                "title": {
                    "query": self.QUICK_BROWN_FOX,
                    "analyzer": "standard"
                }
            }
        }
        self.assertEqual(elasticsearch_query, expected_query)

if __name__ == "__main__":
    unittest.main()
