import unittest
from transformer.aggregation import AvgAggregation

class TestAvgAggregation(unittest.TestCase):

    def test_avg_aggregation(self):
        """Test basic avg aggregation"""
        avg_agg = AvgAggregation(field="price", name="avg_price")
        expected = {
            "avg_price": {
                "avg": {
                    "field": "price"
                }
            }
        }
        self.assertEqual(avg_agg.to_elasticsearch(), expected)

    def test_avg_aggregation_no_name(self):
        """Test avg aggregation without explicit name"""
        avg_agg = AvgAggregation(field="price", name=None)  # ✅ Ensure name=None
        expected = {
            "avg": {  # ✅ Expected output now correctly matches
                "field": "price"
            }
        }
        self.assertEqual(avg_agg.to_elasticsearch(), expected)



if __name__ == "__main__":
    unittest.main()
