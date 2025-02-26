import unittest
from transformer.aggregation import RangeAggregation

class TestRangeAggregation(unittest.TestCase):

    def test_range_aggregation(self):
        """Test range aggregation with valid ranges"""
        range_agg = RangeAggregation(
            field="price", 
            name="price_ranges", 
            ranges=[{"to": 50}, {"from": 50, "to": 100}, {"from": 100}]
        )
        expected = {
            "price_ranges": {
                "range": {
                    "field": "price",
                    "ranges": [
                        {"to": 50},
                        {"from": 50, "to": 100},
                        {"from": 100}
                    ]
                }
            }
        }
        self.assertEqual(range_agg.to_elasticsearch(), expected)

    def test_range_aggregation_invalid(self):
        """Test range aggregation with invalid range (to < from)"""
        with self.assertRaises(ValueError):
            RangeAggregation(field="price", name="price_ranges", ranges=[{"from": 100, "to": 50}])

    def test_range_aggregation_missing_field(self):
        """Ensure an error is raised when no field is provided"""
        with self.assertRaises(ValueError):  # ✅ Now correctly expects ValueError
            RangeAggregation(field=None, name="invalid_range")


    def test_range_aggregation_no_name(self):
        """Test range aggregation without a name"""
        range_agg = RangeAggregation(field="price", ranges=[{"to": 50}, {"from": 50, "to": 100}, {"from": 100}])
        expected = {
            "range": {
                "field": "price",
                "ranges": [
                    {"to": 50},
                    {"from": 50, "to": 100},
                    {"from": 100}
                ]
            }
        }
        self.assertEqual(range_agg.to_elasticsearch(), expected)

if __name__ == "__main__":
    unittest.main()
