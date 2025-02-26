import unittest
from transformer.aggregation import DateHistogramAggregation

class TestDateHistogramAggregation(unittest.TestCase):

    def test_date_histogram_to_elasticsearch(self):
        """Test the standard Elasticsearch JSON output."""
        agg = DateHistogramAggregation(field="timestamp", calendar_interval="1d", format="yyyy-MM-dd", time_zone="UTC")
        expected = {
            "timestamp": {
                "date_histogram": {
                    "field": "timestamp",
                    "calendar_interval": "1d",
                    "format": "yyyy-MM-dd",
                    "time_zone": "UTC"
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_date_histogram_simplified(self):
        """Test simplified aggregation format."""
        agg = DateHistogramAggregation(field="date", interval="1d")  # ✅ This converts to `calendar_interval`
        expected = {
            "date": {
                "date_histogram": {
                    "field": "date",
                    "calendar_interval": "1d"  # ✅ FIXED: Expect `calendar_interval` instead of `interval`
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_date_histogram_with_extended_bounds(self):
        """Test handling of extended_bounds."""
        agg = DateHistogramAggregation(
            field="timestamp",
            calendar_interval="1d",
            extended_bounds={"min": "2023-01-01", "max": "2023-12-31"}
        )
        expected = {
            "timestamp": {
                "date_histogram": {
                    "field": "timestamp",
                    "calendar_interval": "1d",
                    "extended_bounds": {"min": "2023-01-01", "max": "2023-12-31"}
                }
            }
        }
        self.assertEqual(agg.to_elasticsearch(), expected)

    def test_date_histogram_to_json(self):
        """Test JSON serialization."""
        agg = DateHistogramAggregation(
            field="timestamp",
            calendar_interval="1d",
            format="yyyy-MM-dd",
            time_zone="UTC"
        )
        expected_json = {
            "type": "date_histogram_aggregation",
            "field": "timestamp",
            "calendar_interval": "1d",
            "format": "yyyy-MM-dd",
            "time_zone": "UTC"
        }
        self.assertEqual(agg.to_json(), expected_json)

    def test_date_histogram_from_json(self):
        """Test JSON deserialization."""
        json_data = {
            "type": "date_histogram_aggregation",
            "field": "timestamp",
            "calendar_interval": "1d",
            "format": "yyyy-MM-dd",
            "time_zone": "UTC"
        }
        agg = DateHistogramAggregation.from_json(json_data)
        self.assertEqual(agg.field, "timestamp")
        self.assertEqual(agg.calendar_interval, "1d")
        self.assertEqual(agg.format, "yyyy-MM-dd")
        self.assertEqual(agg.time_zone, "UTC")

if __name__ == "__main__":
    unittest.main()
