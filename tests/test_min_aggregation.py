import unittest
from transformer.aggregation import MinAggregation

class TestMinAggregation(unittest.TestCase):

    def test_min_to_elasticsearch(self):
        """Test standard Elasticsearch JSON output."""
        agg = MinAggregation(field="price", name="lowest_price")
        expected = {
            "lowest_price": {
                "min": {
                    "field": "price"
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_min_simplified(self):
        """Test simplified aggregation format."""
        agg = MinAggregation(field="price")
        expected = {
            "price": {
                "min": {
                    "field": "price"
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_min_to_json(self):
        """Test JSON serialization."""
        agg = MinAggregation(field="price", name="lowest_price")
        expected_json = {
            "type": "min_aggregation",
            "field": "price",
            "name": "lowest_price"
        }
        self.assertEqual(agg.to_json(), expected_json)

    def test_min_from_json(self):
        """Test JSON deserialization."""
        json_data = {
            "type": "min_aggregation",
            "field": "price",
            "name": "lowest_price"
        }
        agg = MinAggregation.from_json(json_data)
        self.assertEqual(agg.field, "price")
        self.assertEqual(agg.name, "lowest_price")