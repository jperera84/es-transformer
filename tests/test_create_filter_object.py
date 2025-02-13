import unittest
from transformer import create_filter_object, MatchFilter, TermFilter, RangeFilter, BoolFilter, TermsFilter, WildcardFilter, IdsFilter, MatchPhraseFilter, MultiMatchFilter, QueryStringFilter  # Import necessary components


class TestCreateFilterObject(unittest.TestCase):

    def test_create_filter_object_combined_clauses(self):
        filter_data = [
            {"price": {"gt": 10, "lt": 100}},
            {"category": "Electronics"},
            {"tags": ["new", "featured"]},
            {"date_added": {"gte": "2024-01-01", "lte": "2024-01-31"}},
            {
                "product_name": [
                    {"term": "phone"},
                    {"term": "tablet"},
                    {"term": "laptop"},
                    {"wildcard": "p*one"},
                    {"minimum_should_match": 2}
                ]
            },
            {
                "product_name": {
                    "must_not": [
                        {"term": "out_of_stock"},
                        {"term": "discontinued"}
                    ]
                }
            },
            [
                {"brand": "Samsung"},
                {
                    "color": [
                        {"term": "black"},
                        {"term": "white"},
                        {"minimum_should_match": 1}
                    ]
                }
            ],
            {"product_name": {"match": {"query": "phone case", "fuzziness": "AUTO"}}},
            {"ids": {"values": ["AV456", "BV789", "CV012"]}},
            {
                "product_name": {
                    "multi_match": {
                        "query": "phone case",
                        "fields": ["product_name", "description"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                }
            },
            {
                "product_name": {
                    "multi_match": "phone case"
                }
            },
            {
                "product_name": {
                    "match_phrase": {
                        "query": "red phone case",
                        "slop": 2
                    }
                }
            },
            {
                "product_name": {
                    "query_string": {
                        "query": "phone case (red OR blue)",
                        "default_field": "product_name",
                        "default_operator": "AND",
                        "fuzziness": "AUTO"
                    }
                }
            },
        ]

        filter_objects = create_filter_object(filter_data)
        self.assertIsInstance(filter_objects[0], BoolFilter)  # Top-level AND
        self.assertEqual(filter_objects[0].clause, "must")
        self.assertEqual(len(filter_objects[0].filters), 15)  # Corrected assertion

        # --- Assertions for nested filters (example) ---
        self.assertIsInstance(filter_objects[0].filters[0], RangeFilter)
        self.assertEqual(filter_objects[0].filters[0].field, "price")
        self.assertEqual(filter_objects[0].filters[0].gt, 10)

        self.assertIsInstance(filter_objects[0].filters[1], RangeFilter)
        self.assertEqual(filter_objects[0].filters[1].field, "price")
        self.assertEqual(filter_objects[0].filters[1].lt, 100)

        self.assertIsInstance(filter_objects[0].filters[2], TermFilter)
        self.assertEqual(filter_objects[0].filters[2].field, "category")
        self.assertEqual(filter_objects[0].filters[2].value, "Electronics")

        self.assertIsInstance(filter_objects[0].filters[3], TermsFilter)
        self.assertEqual(filter_objects[0].filters[3].field, "tags")
        self.assertEqual(filter_objects[0].filters[3].terms, ["new", "featured"])

        self.assertIsInstance(filter_objects[0].filters[4], RangeFilter)
        self.assertEqual(filter_objects[0].filters[4].field, "date_added")
        self.assertEqual(filter_objects[0].filters[4].gte, "2024-01-01")

        self.assertIsInstance(filter_objects[0].filters[5], RangeFilter)
        self.assertEqual(filter_objects[0].filters[5].field, "date_added")
        self.assertEqual(filter_objects[0].filters[5].lte, "2024-01-31")

        self.assertIsInstance(filter_objects[0].filters[6], BoolFilter)
        self.assertEqual(filter_objects[0].filters[6].clause, "should")
        self.assertEqual(len(filter_objects[0].filters[6].filters), 4)

        self.assertIsInstance(filter_objects[0].filters[7], BoolFilter)
        self.assertEqual(filter_objects[0].filters[7].clause, "must_not")
        self.assertEqual(len(filter_objects[0].filters[7].filters), 2)

        self.assertIsInstance(filter_objects[0].filters[8], BoolFilter)
        self.assertEqual(filter_objects[0].filters[8].clause, "must")
        self.assertEqual(len(filter_objects[0].filters[8].filters), 2)

        self.assertIsInstance(filter_objects[0].filters[9], MatchFilter)
        self.assertEqual(filter_objects[0].filters[9].field, "product_name")
        self.assertEqual(filter_objects[0].filters[9].query, "phone case")

        self.assertIsInstance(filter_objects[0].filters[10], IdsFilter)
        self.assertEqual(filter_objects[0].filters[10].values, ["AV456", "BV789", "CV012"])

        self.assertIsInstance(filter_objects[0].filters[11], MultiMatchFilter)
        self.assertEqual(filter_objects[0].filters[11].query, "phone case")
        self.assertEqual(filter_objects[0].filters[12].fields, ["product_name"])  # Corrected assertion for simple multi_match

        self.assertIsInstance(filter_objects[0].filters[12], MultiMatchFilter)
        self.assertEqual(filter_objects[0].filters[12].query, "phone case")
        self.assertEqual(filter_objects[0].filters[12].fields, ["product_name"])

        self.assertIsInstance(filter_objects[0].filters[13], MatchPhraseFilter)
        self.assertEqual(filter_objects[0].filters[13].field, "product_name")
        self.assertEqual(filter_objects[0].filters[13].query, "red phone case")

        self.assertIsInstance(filter_objects[0].filters[14], QueryStringFilter)
        self.assertEqual(filter_objects[0].filters[14].query, "phone case (red OR blue)")
        self.assertEqual(filter_objects[0].filters[14].default_field, "product_name")

    def test_create_filter_object_simple_match(self):
        filter_data = [{"product_name": {"match": "phone case"}}]
        filter_objects = create_filter_object(filter_data)
        self.assertIsInstance(filter_objects[0], BoolFilter)
        self.assertEqual(filter_objects[0].clause, "must")
        self.assertEqual(len(filter_objects[0].filters), 1)
        self.assertIsInstance(filter_objects[0].filters[0], MatchFilter)
        self.assertEqual(filter_objects[0].filters[0].field, "product_name")
        self.assertEqual(filter_objects[0].filters[0].query, "phone case")

    def test_create_filter_object_simple_term(self):
        filter_data = [{"category": "Electronics"}]
        filter_objects = create_filter_object(filter_data)
        self.assertIsInstance(filter_objects[0], BoolFilter)
        self.assertEqual(filter_objects[0].clause, "must")

if __name__ == "__main__":
    unittest.main()

        