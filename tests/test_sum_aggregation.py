import unittest
from transformer.aggregation import SumAggregation

class TestSumAggregation(unittest.TestCase):

    def test_sum_to_elasticsearch(self):
        """Test standard Elasticsearch JSON output."""
        agg = SumAggregation(field="price", name="total_price")
        expected = {
            "total_price": {
                "sum": {
                    "field": "price"
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_sum_simplified(self):
        """Test simplified aggregation format."""
        agg = SumAggregation(field="price")
        expected = {
            "price": {
                "sum": {
                    "field": "price"
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_sum_to_json(self):
        """Test JSON serialization."""
        agg = SumAggregation(field="price", name="total_price")
        expected_json = {
            "type": "sum_aggregation",
            "field": "price",
            "name": "total_price"
        }
        self.assertEqual(agg.to_json(), expected_json)

    def test_sum_from_json(self):
        """Test JSON deserialization."""
        json_data = {
            "type": "sum_aggregation",
            "field": "price",
            "name": "total_price"
        }
        agg = SumAggregation.from_json(json_data)
        self.assertEqual(agg.field, "price")
        self.assertEqual(agg.name, "total_price")

