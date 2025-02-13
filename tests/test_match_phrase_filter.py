import unittest
from transformer import MatchPhraseFilter  # Assuming MatchPhraseFilter is in transformer/filter.py

class TestMatchPhraseFilter(unittest.TestCase):

    def test_basic_match_phrase(self):
        match_phrase_filter = MatchPhraseFilter("product_name", "phone case")
        elasticsearch_query = match_phrase_filter.to_elasticsearch()
        expected_query = {"match_phrase": {"product_name": "phone case"}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_match_phrase_with_analyzer(self):
        match_phrase_filter = MatchPhraseFilter("product_name", "phone case", analyzer="standard")
        elasticsearch_query = match_phrase_filter.to_elasticsearch()
        expected_query = {"match_phrase": {"product_name": {"query": "phone case", "analyzer": "standard"}}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_match_phrase_with_boost(self):
        match_phrase_filter = MatchPhraseFilter("product_name", "phone case", boost=2.0)
        elasticsearch_query = match_phrase_filter.to_elasticsearch()
        expected_query = {"match_phrase": {"product_name": {"query": "phone case", "boost": 2.0}}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_match_phrase_with_slop(self):
        match_phrase_filter = MatchPhraseFilter("product_name", "phone case", slop=2)
        elasticsearch_query = match_phrase_filter.to_elasticsearch()
        expected_query = {"match_phrase": {"product_name": {"query": "phone case", "slop": 2}}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_to_json(self):
        match_phrase_filter = MatchPhraseFilter("product_name", "phone case", analyzer="standard", boost=2.0, slop=2)
        json_data = match_phrase_filter.to_json()
        expected_json = {"type": "match_phrase", "field": "product_name", "query": "phone case", "analyzer": "standard", "boost": 2.0, "slop": 2}
        self.assertEqual(json_data, expected_json)

    def test_from_json(self):
        json_data = {"type": "match_phrase", "field": "product_name", "query": "phone case", "analyzer": "standard", "boost": 2.0, "slop": 2}
        match_phrase_filter = MatchPhraseFilter.from_json(json_data)
        self.assertEqual(match_phrase_filter.field, "product_name")
        self.assertEqual(match_phrase_filter.query, "phone case")
        self.assertEqual(match_phrase_filter.analyzer, "standard")
        self.assertEqual(match_phrase_filter.boost, 2.0)
        self.assertEqual(match_phrase_filter.slop, 2)

    def test_from_json_without_optional_params(self):
        json_data = {"type": "match_phrase", "field": "product_name", "query": "phone case"}
        match_phrase_filter = MatchPhraseFilter.from_json(json_data)
        self.assertEqual(match_phrase_filter.field, "product_name")
        self.assertEqual(match_phrase_filter.query, "phone case")
        self.assertIsNone(match_phrase_filter.analyzer)
        self.assertIsNone(match_phrase_filter.boost)
        self.assertIsNone(match_phrase_filter.slop)


if __name__ == "__main__":
    unittest.main()