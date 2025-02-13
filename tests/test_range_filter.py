import unittest
from transformer import RangeFilter  # Assuming RangeFilter is in transformer/filter.py

class TestRangeFilter(unittest.TestCase):

    def test_gt_range_filter(self):
        range_filter = RangeFilter("price", "gt", 100)
        elasticsearch_query = range_filter.to_elasticsearch()
        expected_query = {"range": {"price": {"gt": 100}}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_lt_range_filter(self):
        range_filter = RangeFilter("price", "lt", 50)
        elasticsearch_query = range_filter.to_elasticsearch()
        expected_query = {"range": {"price": {"lt": 50}}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_gte_range_filter(self):
        range_filter = RangeFilter("price", "gte", 0)
        elasticsearch_query = range_filter.to_elasticsearch()
        expected_query = {"range": {"price": {"gte": 0}}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_lte_range_filter(self):
        range_filter = RangeFilter("price", "lte", 1000)
        elasticsearch_query = range_filter.to_elasticsearch()
        expected_query = {"range": {"price": {"lte": 1000}}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_combined_range_filter(self):
        range_filter = RangeFilter("price", "gt", 100)
        range_filter.lt = 500  # Add the 'lt' condition
        elasticsearch_query = range_filter.to_elasticsearch()
        expected_query = {"range": {"price": {"gt": 100, "lt": 500}}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_to_json(self):
        range_filter = RangeFilter("price", "gt", 100)
        json_data = range_filter.to_json()
        expected_json = {"type": "range", "field": "price", "gt": 100}
        self.assertEqual(json_data, expected_json)

    def test_combined_range_to_json(self):
        range_filter = RangeFilter("price", "gt", 100)
        range_filter.lt = 500
        json_data = range_filter.to_json()
        expected_json = {"type": "range", "field": "price", "gt": 100, "lt": 500}
        self.assertEqual(json_data, expected_json)

    def test_from_json(self):
        json_data = {"type": "range", "field": "price", "gt": 100}
        range_filter = RangeFilter.from_json(json_data)
        self.assertEqual(range_filter.field, "price")
        self.assertEqual(range_filter.value, 100)  # Now works!


    def test_combined_range_from_json(self):
        json_data = {"type": "range", "field": "price", "gt": 100, "lt": 500}
        range_filter = RangeFilter.from_json(json_data)
        self.assertEqual(range_filter.field, "price")
        self.assertEqual(range_filter.operator, "gt")
        self.assertEqual(range_filter.value, 100)
        self.assertEqual(range_filter.lt, 500)

    def test_from_json_with_other_operators(self):
        json_data = {"type": "range", "field": "price", "lte": 500, "gte": 100}
        range_filter = RangeFilter.from_json(json_data)
        self.assertEqual(range_filter.field, "price")
        self.assertEqual(range_filter.lte, 500)
        self.assertEqual(range_filter.gte, 100)

if __name__ == "__main__":
    unittest.main()