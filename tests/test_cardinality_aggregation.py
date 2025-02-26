import unittest
from transformer.aggregation import CardinalityAggregation

class TestCardinalityAggregation(unittest.TestCase):

    def test_cardinality_to_elasticsearch(self):
        """Test standard Elasticsearch JSON output."""
        agg = CardinalityAggregation(field="user_id", name="unique_users", precision_threshold=3000)
        expected = {
            "unique_users": {
                "cardinality": {
                    "field": "user_id",
                    "precision_threshold": 3000
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_cardinality_simplified(self):
        """Test simplified aggregation format."""
        agg = CardinalityAggregation(field="user_id")
        expected = {
            "user_id": {
                "cardinality": {
                    "field": "user_id"
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_cardinality_to_json(self):
        """Test JSON serialization."""
        agg = CardinalityAggregation(field="user_id", name="unique_users", precision_threshold=3000)
        expected_json = {
            "type": "cardinality_aggregation",
            "field": "user_id",
            "name": "unique_users",
            "precision_threshold": 3000
        }
        self.assertEqual(agg.to_json(), expected_json)

    def test_cardinality_from_json(self):
        """Test JSON deserialization."""
        json_data = {
            "type": "cardinality_aggregation",
            "field": "user_id",
            "name": "unique_users",
            "precision_threshold": 3000
        }
        agg = CardinalityAggregation.from_json(json_data)
        self.assertEqual(agg.field, "user_id")
        self.assertEqual(agg.name, "unique_users")
        self.assertEqual(agg.precision_threshold, 3000)