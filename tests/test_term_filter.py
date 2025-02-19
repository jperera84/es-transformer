import unittest
from transformer import TermFilter

class TestTermFilter(unittest.TestCase):

    def test_basic_term(self):
        term_filter = TermFilter("status", "active")
        expected_query = {"term": {"status": {"value": "active"}}}
        self.assertEqual(term_filter.to_elasticsearch(), expected_query)

    def test_term_with_boost(self):
        term_filter = TermFilter("status", "active", boost=2.0)
        expected_query = {"term": {"status": {"value": "active", "boost": 2.0}}}
        self.assertEqual(term_filter.to_elasticsearch(), expected_query)

    def test_term_case_insensitive(self):
        term_filter = TermFilter("role", "Admin", case_insensitive=True)
        expected_query = {"term": {"role": {"value": "Admin", "case_insensitive": True}}}
        self.assertEqual(term_filter.to_elasticsearch(), expected_query)

    def test_to_json(self):
        term_filter = TermFilter("status", "active", boost=1.5, case_insensitive=True)
        expected_json = {
            "type": "term",
            "field": "status",
            "value": "active",
            "boost": 1.5,
            "case_insensitive": True
        }
        self.assertEqual(term_filter.to_json(), expected_json)

    def test_from_json(self):
        json_data = {
            "type": "term",
            "field": "status",
            "value": "active",
            "boost": 1.5,
            "case_insensitive": True
        }
        term_filter = TermFilter.from_json(json_data)
        self.assertEqual(term_filter.field, "status")
        self.assertEqual(term_filter.value, "active")
        self.assertEqual(term_filter.boost, 1.5)
        self.assertTrue(term_filter.case_insensitive)


if __name__ == "__main__":
    unittest.main()