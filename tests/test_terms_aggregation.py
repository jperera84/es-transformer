import unittest
from transformer import TermsAggregation, AvgAggregation, MinAggregation, MaxAggregation, CardinalityAggregation
import json

class TestTermsAggregation(unittest.TestCase):
    def test_terms_aggregation_to_elasticsearch(self):
        agg = TermsAggregation("category")
        expected = {'terms': {'field': 'category', 'size': 10}}
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_terms_aggregation_with_size(self):
        agg = TermsAggregation("category", size=20)
        expected = {"terms": {"field": "category", "size": 20}}  # Correct expected output
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_terms_aggregation_with_order(self):
        agg = TermsAggregation("category", order={"_count": "desc"})
        expected = {"terms": {"field": "category", "size": 10, "order": {"_count": "desc"}}}
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_terms_aggregation_with_nested_aggs(self):
        agg = TermsAggregation(name="my_agg_name", field="category", size=10, aggs={
            "my_sub_agg_name": {
                "avg": {"field": "price"}
            },
            "product_count": {
                "cardinality": {"field": "product_id"} # Example of another nested aggregation
            }}
        )
        expected = {
            "my_agg_name": {
                "terms": {
                    "field": "category",
                    "size": 10
                },
                "aggs": {
                    "my_sub_agg_name": {
                        "avg": {
                            "field": "price"
                        }
                    },
                    "product_count": {
                        "cardinality": {
                            "field": "product_id"
                        }
                    }
                }
            }
        }
        self.assertDictEqual(agg.to_elasticsearch(), expected)

    def test_terms_aggregation_with_min_doc_count(self): # New Test
        agg = TermsAggregation("category", min_doc_count=5)
        expected = {"terms": {"field": "category", "size": 10, "min_doc_count": 5}}
        self.assertEqual(agg.to_elasticsearch(), expected)
