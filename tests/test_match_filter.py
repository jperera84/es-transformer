import unittest
from transformer import MatchFilter

class TestMatchFilter(unittest.TestCase):

    QUICK_BROWN_FOX = "quick brown fox"

    def test_basic_match(self):
        match_filter = MatchFilter("title", self.QUICK_BROWN_FOX)
        self.assertEqual(
            match_filter.to_elasticsearch(),
            {"match": {"title": {"query": self.QUICK_BROWN_FOX}}}
        )

    def test_match_with_analyzer(self):
        match_filter = MatchFilter("title", self.QUICK_BROWN_FOX, analyzer="standard")
        self.assertEqual(
            match_filter.to_elasticsearch(),
            {"match": {"title": {"query": self.QUICK_BROWN_FOX, "analyzer": "standard"}}}
        )

if __name__ == "__main__":
    unittest.main()