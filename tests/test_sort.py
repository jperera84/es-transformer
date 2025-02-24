import unittest
from transformer import Sort

class TestSortClass(unittest.TestCase):

    def test_sort_to_elasticsearch_simple(self):
        sort_obj = Sort("product_name")
        expected = {"product_name": {"order": "asc"}}
        self.assertEqual(sort_obj.to_elasticsearch(), expected)

    def test_sort_to_elasticsearch_desc(self):
        sort_obj = Sort("price", order="desc")
        expected = {"price": {"order": "desc"}}
        self.assertEqual(sort_obj.to_elasticsearch(), expected)

    def test_sort_to_elasticsearch_score(self):
        sort_obj = Sort("_score", order="desc")
        expected = {"_score": {"order": "desc"}}
        self.assertEqual(sort_obj.to_elasticsearch(), expected)

    def test_sort_to_elasticsearch_script(self):
        sort_obj = Sort("my_field", script="doc['my_field'].value * 2", lang="painless", type="number", order="desc")
        expected = {"_script": {"script": {"source": "doc['my_field'].value * 2", "lang": "painless"}, "type": "number", "order": "desc"}}
        self.assertEqual(sort_obj.to_elasticsearch(), expected)

    def test_sort_to_elasticsearch_nested(self):
        sort_obj = Sort(field="nested.field", order="asc", nested_path="nested")
        expected = {
            "nested.field": {
                "order": "asc",
                "nested": {  # ✅ Correct placement of nested path
                    "path": "nested"
                }
            }
        }
        self.assertEqual(sort_obj.to_elasticsearch(), expected)


    def test_sort_to_elasticsearch_missing(self):
        sort_obj = Sort("date", missing="_last")
        expected = {"date": {"order": "asc", "missing": "_last"}}
        self.assertEqual(sort_obj.to_elasticsearch(), expected)

    def test_sort_to_elasticsearch_unmapped(self):
        sort_obj = Sort("nonexistent_field", unmapped_type="keyword")
        expected = {"nonexistent_field": {"order": "asc", "unmapped_type": "keyword"}}
        self.assertEqual(sort_obj.to_elasticsearch(), expected)

    def test_sort_to_json(self):
        sort_obj = Sort("product_name", order="desc", mode="min", format="date_time", numeric_type="double", nested_path="nested_object", nested_filter={"term": {"nested_field": "value"}}, missing="_last", unmapped_type="integer", script="doc['my_field'].value + params.value", lang="painless", params={"value": 5}, type="number")
        expected_json = {
            "type": "sort", "field": "product_name", "order": "desc", "mode": "min", "format": "date_time",
            "numeric_type": "double", "nested_path": "nested_object", "nested_filter": {"term": {"nested_field": "value"}},
            "missing": "_last", "unmapped_type": "integer", "script": "doc['my_field'].value + params.value",
            "lang": "painless", "params": {"value": 5}, "type": "number"
        }
        self.assertEqual(sort_obj.to_json(), expected_json)

    def test_sort_from_json(self):
        json_data = {
            "type": "sort", "field": "product_name", "order": "desc", "mode": "min", "format": "date_time",
            "numeric_type": "double", "nested_path": "nested_object", "nested_filter": {"term": {"nested_field": "value"}},
            "missing": "_last", "unmapped_type": "integer", "script": "doc['my_field'].value + params.value",
            "lang": "painless", "params": {"value": 5}, "type": "number"
        }
        sort_obj = Sort.from_json(json_data)
        self.assertEqual(sort_obj.field, "product_name")
        self.assertEqual(sort_obj.order, "desc")
        self.assertEqual(sort_obj.mode, "min")
        self.assertEqual(sort_obj.format, "date_time")
        self.assertEqual(sort_obj.numeric_type, "double")
        self.assertEqual(sort_obj.nested_path, "nested_object")
        self.assertEqual(sort_obj.nested_filter, {"term": {"nested_field": "value"}})
        self.assertEqual(sort_obj.missing, "_last")
        self.assertEqual(sort_obj.unmapped_type, "integer")
        self.assertEqual(sort_obj.script, "doc['my_field'].value + params.value")
        self.assertEqual(sort_obj.lang, "painless")
        self.assertEqual(sort_obj.params, {"value": 5})
        self.assertEqual(sort_obj.type, "number")

if __name__ == '__main__':
    unittest.main()