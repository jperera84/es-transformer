import unittest
from transformer.aggregation import TermsAggregation

class TestTermsAggregation(unittest.TestCase):

    def test_traditional_terms_aggregation(self):
        """Test traditional terms aggregation structure."""
        agg = TermsAggregation(field="category", name="category_terms", size=20)
        expected = {
            "category_terms": {
                "terms": {
                    "field": "category",
                    "size": 20  # ✅ Ensure correct size placement
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_simplified_terms_aggregation(self):
        """Test simplified terms aggregation format."""
        agg = TermsAggregation(field="category", size=20)
        expected = {
            "category": {  # ✅ Ensure field name wraps the aggregation
                "terms": {
                    "field": "category",
                    "size": 20
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_invalid_format(self):
        """Test that invalid format raises a TypeError"""
        with self.assertRaises(TypeError):  # ✅ Ensure invalid format raises an error
            TermsAggregation(field=None, name="invalid")



if __name__ == "__main__":
    unittest.main()

