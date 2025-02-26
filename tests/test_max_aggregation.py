import unittest
from transformer.aggregation import MaxAggregation

class TestMaxAggregation(unittest.TestCase):

    def test_max_to_elasticsearch(self):
        """Test standard Elasticsearch JSON output."""
        agg = MaxAggregation(field="price", name="highest_price")
        expected = {
            "highest_price": {
                "max": {
                    "field": "price"
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_max_simplified(self):
        """Test simplified aggregation format."""
        agg = MaxAggregation(field="price")
        expected = {
            "price": {
                "max": {
                    "field": "price"
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_max_to_json(self):
        """Test JSON serialization."""
        agg = MaxAggregation(field="price", name="highest_price")
        expected_json = {
            "type": "max_aggregation",
            "field": "price",
            "name": "highest_price"
        }
        self.assertEqual(agg.to_json(), expected_json)

    def test_max_from_json(self):
        """Test JSON deserialization."""
        json_data = {
            "type": "max_aggregation",
            "field": "price",
            "name": "highest_price"
        }
        agg = MaxAggregation.from_json(json_data)
        self.assertEqual(agg.field, "price")
        self.assertEqual(agg.name, "highest_price")
