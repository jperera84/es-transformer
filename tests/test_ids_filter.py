import unittest
from transformer import IdsFilter  # Assuming IdsFilter is in transformer/filter.py

class TestIdsFilter(unittest.TestCase):

    def test_integer_ids(self):
        ids_filter = IdsFilter([1, 2, 3])
        elasticsearch_query = ids_filter.to_elasticsearch()
        expected_query = {"ids": {"values": [1, 2, 3]}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_string_ids(self):
        ids_filter = IdsFilter(["id1", "id2", "id3"])
        elasticsearch_query = ids_filter.to_elasticsearch()
        expected_query = {"ids": {"values": ["id1", "id2", "id3"]}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_mixed_ids(self):
        ids_filter = IdsFilter([1, "id2", 3])
        elasticsearch_query = ids_filter.to_elasticsearch()
        expected_query = {"ids": {"values": [1, "id2", 3]}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_type_parameter(self):
        ids_filter = IdsFilter([1, 2, 3], type="product")
        elasticsearch_query = ids_filter.to_elasticsearch()
        expected_query = {"ids": {"type": "product", "values": [1, 2, 3]}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_empty_ids_list(self):
        ids_filter = IdsFilter([])
        elasticsearch_query = ids_filter.to_elasticsearch()
        expected_query = {"ids": {"values": []}}
        self.assertEqual(elasticsearch_query, expected_query)

    def test_to_json(self):
        ids_filter = IdsFilter([1, 2, 3], type="product")
        json_data = ids_filter.to_json()
        expected_json = {"type": "ids", "values": [1, 2, 3], "type_name": "product"}
        self.assertEqual(json_data, expected_json)

    def test_from_json(self):
        json_data = {"type": "ids", "values": [1, 2, 3], "type_name": "product"}
        ids_filter = IdsFilter.from_json(json_data)
        self.assertEqual(ids_filter.values, [1, 2, 3])
        self.assertEqual(ids_filter.type, "product")

    def test_from_json_without_type(self):
        json_data = {"type": "ids", "values": [1, 2, 3]}
        ids_filter = IdsFilter.from_json(json_data)
        self.assertEqual(ids_filter.values, [1, 2, 3])
        self.assertIsNone(ids_filter.type)

if __name__ == "__main__":
    unittest.main()