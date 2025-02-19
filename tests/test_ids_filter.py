import unittest
from transformer.filter import IdsFilter  # Ensure correct import path

class TestIdsFilter(unittest.TestCase):

    def test_integer_ids(self):
        ids_filter = IdsFilter([1, 2, 3])
        self.assertEqual(ids_filter.to_elasticsearch(), {"ids": {"values": [1, 2, 3]}})

    def test_string_ids(self):
        ids_filter = IdsFilter(["id1", "id2", "id3"])
        self.assertEqual(ids_filter.to_elasticsearch(), {"ids": {"values": ["id1", "id2", "id3"]}})

    def test_mixed_ids(self):
        ids_filter = IdsFilter([1, "id2", 3])
        self.assertEqual(ids_filter.to_elasticsearch(), {"ids": {"values": [1, "id2", 3]}})

    def test_empty_ids_list(self):
        ids_filter = IdsFilter([])
        self.assertEqual(ids_filter.to_elasticsearch(), {"ids": {"values": []}})

    def test_to_json(self):
        ids_filter = IdsFilter([1, 2, 3])
        self.assertEqual(
            ids_filter.to_json(),
            {"type": "ids", "values": [1, 2, 3]}
        )

    def test_from_json(self):
        json_data = {"type": "ids", "values": [1, 2, 3]}
        ids_filter = IdsFilter.from_json(json_data)
        self.assertEqual(ids_filter.values, [1, 2, 3])

if __name__ == "__main__":
    unittest.main()
