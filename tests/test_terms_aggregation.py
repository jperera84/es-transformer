import unittest
from transformer.aggregation import TermsAggregation, create_single_aggregation_object

class TestTermsAggregation(unittest.TestCase):

    def test_traditional_terms_aggregation(self):
        agg_def = {"terms": {"field": "category", "size": 20}}
        agg = create_single_aggregation_object(agg_def, name="category_terms")
        expected = {"category_terms": {"terms": {"field": "category", "size": 20}}}
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_simplified_terms_aggregation(self):
        agg_def = ["terms", 20]  # Simplified format
        agg = create_single_aggregation_object(agg_def, name="category")
        expected = {"category": {"terms": {"field": "category", "size": 20}}}
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_invalid_format(self):
        """Test that invalid format raises a TypeError"""
        with self.assertRaises(TypeError):  # ✅ Now correctly expects TypeError
            TermsAggregation(field=123, size="wrong")  # Invalid format: field should be string, size should be int


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
