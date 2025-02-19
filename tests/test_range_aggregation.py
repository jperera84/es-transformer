import unittest
from transformer import RangeAggregation, AvgAggregation, MinAggregation  # Import necessary classes

class TestRangeAggregation(unittest.TestCase):

    def test_range_aggregation_basic(self):
        agg = RangeAggregation(field="price", name="price_range", ranges=[{"to": 50}, {"from": 50, "to": 100}, {"from": 100}])
        expected = {
            "price_range": {
                "range": {
                    "price": {
                        "to": 50,
                        "from": 50,
                        "to": 100,
                        "from": 100
                    }
                }
            }
        }
        self.assertDictEqual(agg.to_elasticsearch(), expected)

    def test_range_aggregation_with_keys(self):
        agg = RangeAggregation(
            field="age",
            name="age_range",
            ranges=[
                {"key": "young", "to": 20},
                {"key": "adult", "from": 20, "to": 60},
                {"key": "senior", "from": 60}
            ]
        )
        expected = {
            "age_range": {
                "range": {
                    "age": {
                        "key": "young",
                        "to": 20,
                        "key": "adult",
                        "from": 20,
                        "to": 60,
                        "key": "senior",
                        "from": 60
                    }
                }
            }
        }
        self.assertDictEqual(agg.to_elasticsearch(), expected)

    def test_range_aggregation_with_nested_aggs(self):
        agg = RangeAggregation(
            field="price",
            name="price_range",
            ranges=[{"to": 50}, {"from": 50, "to": 100}],
            aggs={"avg_price": AvgAggregation(field="price", name="avg_price")}  # Name the nested aggregation
        )
        expected = {
            "price_range": {
                "range": {
                    "price": {
                        "to": 50,
                        "from": 50,
                        "to": 100
                    }
                },
                "aggs": {"avg_price": {"avg_price": {"avg": {"field": "price"}}}} # Match the name
            }
        }
        self.assertDictEqual(agg.to_elasticsearch(), expected)

    def test_range_aggregation_with_nested_path_and_filter(self):
        agg = RangeAggregation(
            field="product.price",
            name="product_price_range",
            ranges=[{"to": 50}, {"from": 50, "to": 100}],
            nested_path="product",
            nested_filter={"term": {"product.category": "electronics"}}
        )
        expected = {
            "product_price_range": {
                "nested": {
                    "path": "product",
                    "filter": {"term": {"product.category": "electronics"}},
                    "aggs": {
                        "product_price_range": {
                            "range": {
                                "product.price": {
                                    "from": 50,  # from before to
                                    "to": 50,
                                    "from": 100, #from before to
                                    "to": 100
                                }
                            }
                        }
                    }
                }
            }
        }
        query = str(agg.to_elasticsearch())
        self.assertDictEqual(agg.to_elasticsearch(), expected)

    def test_range_aggregation_with_all_options(self):
        agg = RangeAggregation(
            field="price",
            name="price_range",
            ranges=[{"key": "cheap", "to": 50}, {"key": "medium", "from": 50, "to": 100}],
            nested_path="product",
            nested_filter={"term": {"product.category": "electronics"}},
            aggs={"min_price": MinAggregation(field="price")}
        )
        expected = {
            "price_range": {
                "range": {
                    "price": {
                        "key": "cheap",
                        "to": 50,
                        "key": "medium",
                        "from": 50,
                        "to": 100
                    }
                },
                "nested_path": "product",
                "nested_filter": {"term": {"product.category": "electronics"}},
                "aggs": {"min_price": {"min": {"field": "price"}}}
            }
        }
        self.assertDictEqual(agg.to_elasticsearch(), expected)

    def test_range_aggregation_invalid_ranges(self):
        with self.assertRaises(ValueError):
            RangeAggregation(field="price", ranges=[{"to": 50, "from": 60}])  # Invalid range

        with self.assertRaises(ValueError):
            RangeAggregation(field="price", ranges=[{"to": 50, "to": 60}])  # Duplicate "to"

        with self.assertRaises(ValueError):
            RangeAggregation(field="price", ranges=[{"from": 60, "from": 50}])  # Duplicate "from"

        with self.assertRaises(ValueError):
            RangeAggregation(field="price", ranges=[{"key": "test", "key": "test"}])  # Duplicate "key"