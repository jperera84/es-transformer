from flask import Blueprint
from transformer import transform
import json

home_route = Blueprint('home_route', __name__)

@home_route.route("/", methods=["GET"])
def home():
    transformer = transform.Transformer("my_index")
    query = transformer.transform(
        {
            "size": 20,
            "filters": [
                {"price": {"gt": 10, "lt": 100}},  # AND condition (implicit)
                {"category": "Electronics"},
                {"tags": ["new", "featured"]},
                {"date_added": {"gte": "2024-01-01", "lte": "2024-01-31"}},
                { # OR condition
                    "product_name": [
                        {"term": "phone"},
                        {"term": "tablet"},
                        {"term": "laptop"},
                        {"wildcard": "p*one"}, # Wildcard as another option
                        {"minimum_should_match": 2}
                    ]
                },
                {
                    "product_name": {
                        "must_not": [  # NOT condition
                            {"term": "out_of_stock"},
                            {"term": "discontinued"}
                        ]
                    }
                },
                [  # AND condition with nested OR
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
                        "multi_match": "phone case" # simple multi_match with default parameters
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
            ],
            "sorts": [
                {"field": "price", "order": "desc"},
                {"field": "date_added", "order": "asc", "format": "yyyy-MM-dd"},
                {"field": "sales", "order": "asc", "mode": "avg", "numeric_type": "long", "missing": "_last", "unmapped_type": "long"},
                {"field": "_score", "order": "desc"},  # Special case for _score
                {"field": "nested_object.field1", "order": "asc", "nested_path":"nested_object"}, # Sort by field1 within nested_object
                {"field": "nested_object.field2", "order": "desc", "nested_path":"nested_object", "nested_filter": {"term": {"nested_object.active": True}}}, # Sort by field2 with a filter
                {"field": "_script", "order": "asc", "script": "doc['field_name'].value * 1.2", "lang":"painless", "params":{"factor": 1.1}, "type":"number"}  # Script sort
            ],
            "aggs": {
                "terms_agg": {"terms": {"field": "category", "size": 20}},
                "avg_agg": {"avg": {"field": "price"}},
                "range_agg": {"range": {"field": "price", "ranges": [{"to": 50}, {"from": 50, "to": 100}, {"from": 100}]}},
                "hist_agg": {"histogram": {"field": "price", "interval": 20}},
                "date_hist_agg": {"date_histogram": {"field": "date", "interval": "1d"}},
                "sum_agg": {"sum": {"field": "price"}},
                "min_agg": {"min": {"field": "price"}},
                "max_agg": {"max": {"field": "price"}},
                "my_agg_name": {  # Aggregation name
                    "terms": {  # Aggregation type
                        "field": "category",
                        "size": 10,
                        "aggs": {  # Nested aggregations
                            "my_sub_agg_name": {
                                "avg": {"field": "price"}
                            },
                            "product_count": {
                                "cardinality": {"field": "product_id"} # Example of another nested aggregation
                            }
                        }
                    }
                },
                "my_composite_agg_no_naming": {
                    "composite": {
                        "sources": [
                            {"terms": {"field": "category"}},  # No name for this source
                            {"histogram": {"field": "price", "interval": 50}},  # No name for this source
                        ],
                        "size": 20,
                        "order": {  # Order is now a dictionary using _key
                            "_key": "asc",  # Sort by the combined key of all sources
                        },
                    }
                },
                "my_composite_agg_naming": {
                    "composite": {
                        "sources": [
                            {"name": "category_terms", "terms": {"field": "category"}},  # Named source - CORRECTED
                            {"name": "price_histogram", "histogram": {"field": "price", "interval": 50}},  # Named source - CORRECTED
                        ],
                        "size": 20,
                        "order": {  # Order is now a dictionary using source names
                            "category_terms": "asc",  # Sort by the named source "category_terms"
                            "price_histogram": "desc"  # Sort by the named source "price_histogram"
                        },
                    }
                },
                "my_composite_agg_paginated": {
                    "composite": {
                        "sources": [
                            {"terms": {"field": "category"}},
                            {"histogram": {"field": "price", "interval": 50}},
                        ],
                        "size": 20,
                        "after": {"category": "some_category", "price": 100}, # Use after_key for pagination
                    }
                }
            }
        }
    )
    return prettify_query(query)

def prettify_query(query):
    """Prettifies a nested dictionary (like an Elasticsearch query) as JSON."""
    return json.dumps(query, indent=2)  # Use json.dumps with indentation