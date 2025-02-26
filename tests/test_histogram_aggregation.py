import unittest
from transformer.aggregation import HistogramAggregation

class TestHistogramAggregation(unittest.TestCase):
    
    def test_histogram_aggregation(self):
        agg = HistogramAggregation(field="price", interval=20, name="price_histogram")
        expected = {
            "price_histogram": {
                "histogram": {
                    "field": "price",
                    "interval": 20
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_histogram_aggregation_simplified(self):
        agg = HistogramAggregation(field="price", interval=10)
        expected = {
            "histogram": {
                "field": "price",
                "interval": 10
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_histogram_to_json(self):
        agg = HistogramAggregation(field="price", interval=10, name="price_histogram")
        expected_json = {
            "type": "histogram_aggregation",
            "field": "price",
            "name": "price_histogram",
            "interval": 10,
            "nested_path": None,
            "nested_filter": None
        }
        self.assertDictEqual(agg.to_json(), expected_json)

    def test_histogram_from_json(self):
        json_data = {
            "type": "histogram_aggregation",
            "field": "price",
            "name": "price_histogram",
            "interval": 10,
            "nested_path": None,
            "nested_filter": None
        }
        agg = HistogramAggregation.from_json(json_data)
        self.assertEqual(agg.field, "price")
        self.assertEqual(agg.name, "price_histogram")
        self.assertEqual(agg.interval, 10)

if __name__ == "__main__":
    unittest.main()
