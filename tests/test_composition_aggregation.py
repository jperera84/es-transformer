import unittest
from transformer.aggregation import CompositeAggregation

class TestCompositeAggregation(unittest.TestCase):

    def test_composite_to_elasticsearch(self):
        """Test standard Elasticsearch JSON output."""
        agg = CompositeAggregation(
            name="composite_example",
            sources=[
                {"name": "category_terms", "terms": {"field": "category"}},
                {"name": "price_histogram", "histogram": {"field": "price", "interval": 50}}
            ],
            size=20,
            order={"category_terms": "asc", "price_histogram": "desc"},
            after={"category": "some_category", "price": 100}
        )

        expected = {
            "composite_example": {
                "composite": {
                    "sources": [
                        {"name": "category_terms", "terms": {"field": "category"}},
                        {"name": "price_histogram", "histogram": {"field": "price", "interval": 50}}
                    ],
                    "size": 20,
                    "order": {"category_terms": "asc", "price_histogram": "desc"},
                    "after": {"category": "some_category", "price": 100}
                }
            }
        }

        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_composite_simplified(self):
        """Test simplified aggregation format."""
        agg = CompositeAggregation(
            sources=[
                {"name": "category_terms", "terms": {"field": "category"}},
                {"name": "price_histogram", "histogram": {"field": "price", "interval": 50}}
            ]
        )

        expected = {
            "composite": {
                "sources": [
                    {"name": "category_terms", "terms": {"field": "category"}},
                    {"name": "price_histogram", "histogram": {"field": "price", "interval": 50}}
                ],
                "size": 10  # Default size
            }
        }

        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_composite_to_json(self):
        """Test JSON serialization."""
        agg = CompositeAggregation(
            name="composite_example",
            sources=[
                {"name": "category_terms", "terms": {"field": "category"}},
                {"name": "price_histogram", "histogram": {"field": "price", "interval": 50}}
            ],
            size=20,
            after={"category": "some_category", "price": 100},
            order={"category_terms": "asc", "price_histogram": "desc"}
        )

        expected_json = {
            "type": "composite_aggregation",
            "name": "composite_example",
            "sources": [
                {"name": "category_terms", "terms": {"field": "category"}},
                {"name": "price_histogram", "histogram": {"field": "price", "interval": 50}}
            ],
            "size": 20,
            "order": {"category_terms": "asc", "price_histogram": "desc"},
            "after": {"category": "some_category", "price": 100}
        }

        self.assertEqual(agg.to_json(), expected_json)

    def test_composite_from_json(self):
        """Test JSON deserialization."""
        json_data = {
            "type": "composite_aggregation",
            "name": "composite_example",
            "sources": [
                {"name": "category_terms", "terms": {"field": "category"}},
                {"name": "price_histogram", "histogram": {"field": "price", "interval": 50}}
            ],
            "size": 20,
            "order": {"category_terms": "asc", "price_histogram": "desc"},
            "after": {"category": "some_category", "price": 100}
        }

        agg = CompositeAggregation.from_json(json_data)

        self.assertEqual(agg.name, "composite_example")
        self.assertEqual(agg.sources, [
            {"name": "category_terms", "terms": {"field": "category"}},
            {"name": "price_histogram", "histogram": {"field": "price", "interval": 50}}
        ])
        self.assertEqual(agg.size, 20)
        self.assertEqual(agg.order, {"category_terms": "asc", "price_histogram": "desc"})
        self.assertEqual(agg.after, {"category": "some_category", "price": 100})
