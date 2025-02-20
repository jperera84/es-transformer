import unittest
from transformer.filter import RangeFilter

class TestRangeFilter(unittest.TestCase):

    def test_gt_range_filter(self):
        range_filter = RangeFilter("price", gt=100)
        self.assertEqual(
            range_filter.to_elasticsearch(),
            {"range": {"price": {"gt": 100}}}
        )

    def test_lt_range_filter(self):
        range_filter = RangeFilter("price", lt=50)
        self.assertEqual(
            range_filter.to_elasticsearch(),
            {"range": {"price": {"lt": 50}}}
        )

    def test_gte_range_filter(self):
        range_filter = RangeFilter("price", gte=0)
        self.assertEqual(
            range_filter.to_elasticsearch(),
            {"range": {"price": {"gte": 0}}}
        )

    def test_lte_range_filter(self):
        range_filter = RangeFilter("price", lte=1000)
        self.assertEqual(
            range_filter.to_elasticsearch(),
            {"range": {"price": {"lte": 1000}}}
        )

    def test_combined_range_filter(self):
        range_filter = RangeFilter("price", gt=100, lt=500)
        self.assertEqual(
            range_filter.to_elasticsearch(),
            {"range": {"price": {"gt": 100, "lt": 500}}}
        )

    def test_to_json(self):
        range_filter = RangeFilter("price", gt=100, lt=500)
        self.assertEqual(
            range_filter.to_json(),
            {"type": "range", "field": "price", "gt": 100, "lt": 500}
        )

    def test_from_json(self):
        json_data = {"field": "price", "gt": 100, "lt": 500}  # Removed "type"
        range_filter = RangeFilter.from_json(json_data)
        self.assertEqual(range_filter.field, "price")
        self.assertEqual(range_filter.conditions["gt"], 100)
        self.assertEqual(range_filter.conditions["lt"], 500)

    def test_invalid_operator(self):
        """Ensures that an invalid range operator raises a ValueError"""
        with self.assertRaises(ValueError):
            RangeFilter("price", between=100)  # 'between' is not a valid operator

    def test_from_json_with_invalid_type(self):
        json_data = {"type": "range", "field": "price", "gt": 100, "lt": 500}
        with self.assertRaises(ValueError):
            RangeFilter.from_json(json_data)

if __name__ == "__main__":
    unittest.main()
