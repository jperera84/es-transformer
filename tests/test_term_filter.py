import unittest
from transformer import TermFilter  # Assuming TermFilter is in transformer/filter.py

class TestTermFilter(unittest.TestCase):

    def test_basic_term(self):
        term_filter = TermFilter("status", "active")
        elasticsearch_query = term_filter.to_elasticsearch()
        expected_query = {
            "term": {
                "status": "active"
            }
        }
        self.assertEqual(elasticsearch_query, expected_query)

    def test_term_with_boost(self):
        term_filter = TermFilter("status", "active", boost=1.5)
        elasticsearch_query = term_filter.to_elasticsearch()
        expected_query = {
            "term": {
                "status": {
                    "value": "active",
                    "boost": 1.5
                }
            }
        }
        self.assertEqual(elasticsearch_query, expected_query)

    def test_term_case_insensitive(self):
        """✅ FIX: Ensure case_insensitive is handled correctly"""
        term_filter = TermFilter("role", "Admin", case_insensitive=True)
        elasticsearch_query = term_filter.to_elasticsearch()
        expected_query = {
            "term": {
                "role": {
                    "value": "Admin",
                    "case_insensitive": True
                }
            }
        }
        self.assertEqual(elasticsearch_query, expected_query)

    def test_to_json(self):
        """✅ FIX: Ensure JSON output includes case_insensitive when present"""
        term_filter = TermFilter("status", "active", boost=1.5, case_insensitive=True)
        json_data = term_filter.to_json()
        expected_json = {
            "type": "term",
            "field": "status",
            "value": "active",
            "boost": 1.5,
            "case_insensitive": True
        }
        self.assertEqual(json_data, expected_json)

    def test_from_json(self):
        """✅ FIX: Ensure `from_json` correctly restores `case_insensitive`"""
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
        self.assertTrue(term_filter.case_insensitive)  # ✅ This test was previously failing

if __name__ == "__main__":
    unittest.main()
