def generate_ids_filter_object():
    return {
        "filters": [
            { "ids": ["1", "2"] }
        ]
    }

def generate_match_filter_object():
    return {
        "filters": {  # Dictionary → OR condition
            "formula_metadata.name": [
                "Threat Detection Rule",
                "Suspicious Upload Rule"
            ]  # OR condition (should)
        }
    }

def generate_range_filter_object():
    return {
        "filters": [
            { "action_count": { "gt": 5, "lt": 20 } },  # ✅ Adjusted to a valid field
            { "client_access_id": { "gte": 100000000, "lte": 500000000 } }  # ✅ Another valid range
        ]
    }

def generate_term_filter_object():
    return {
        "filters": [
            { "formula_matches_action_archiving_state.type": "archived" },  # ✅ Inferred as `term`
            { "client_id": 987654321 },  # ✅ Inferred as `term`
            { "event.provider": "security-monitor" }
        ]
    }

def generate_terms_filter_object():
    return {
        "filters": [
            { "formula_metadata.tags.value": ["security", "critical"] },  # ✅ Inferred as `terms`
        ]
    }

def generate_wildcard_filter_object():
    return {
        "filters": [
            { "event.provider": { "wildcard": "security*" } }  # ✅ Wildcard for keyword field
        ]
    }

def generate_bool_filter_object():
    return {
        "filters": [
            [  # ✅ AND condition (implicit must)
                {"formula_metadata.name": "Threat Detection Rule"},  # ✅ Term filter for `name`
                {  # ✅ OR condition (should)
                    "formula_metadata.tags.value": [
                        "security",
                        "critical"
                    ]
                }
            ]
        ]
    }

def generate_sort_object():
    return {
        "filters": [
            { "ids": ["xxxxxxx", "000000000"] }
        ],
        "sorts": [
            # ✅ Basic field sorting (ascending)
            { "field": "price", "order": "asc" },

            # ✅ Field sorting (descending)
            { "field": "rating", "order": "desc" },

            # ✅ Sorting with `missing` parameter
            { "field": "created_at", "order": "asc", "missing": "_last" },

            # ✅ Sorting with `mode`
            { "field": "popularity", "order": "desc", "mode": "max" },

            # ✅ Sorting with `unmapped_type`
            { "field": "category", "order": "asc", "unmapped_type": "keyword" },

            # ✅ Nested field sorting
            { "field": "nested.field", "order": "asc", "nested_path": "nested" },

            # ✅ Script-based sorting
            {
                "field": "_script",
                "order": "desc",
                "script": "doc['my_field'].value * 2",
                "type": "number"
            },

            # ✅ Nested sorting with filter
            {
                "field": "reviews.rating",
                "order": "desc",
                "nested_path": "reviews",
                "nested_filter": {
                    "term": { "reviews.verified": True }
                }
            }
        ]
    }

def generate_terms_agg_object():
    return {
        "aggs": {
            "category": ["terms", 20]  # ["AggregationType", Size]
        }
    }

def generate_avg_agg_object():
    return {
        "aggs": {
            "avg_price": ["avg", "price"]  # ✅ Simplified format: ["aggregation_type", field_name]
        }
    }

def generate_range_agg_object():
    return {
        "aggs": {
            "price": ["range", [{"to": 50}, {"from": 50, "to": 100}, {"from": 100}]]  # ✅ Correct field reference
        }
    }

def generate_histogram_agg_object():
    return {
        "aggs": {
            "price_histogram": ["histogram", 20, {"min": 0, "max": 1000}, 1, True]  # ✅ Includes optional params
        }
    }

def generate_date_histogram_agg_object():
    return {
        "aggs": {
            "date_histogram_agg": ["date_histogram", "1d"],  # ✅ Simplified format
            "custom_date_histogram": {
                "date_histogram": {
                    "field": "timestamp",
                    "calendar_interval": "1d",
                    "format": "yyyy-MM-dd",
                    "time_zone": "UTC",
                    "min_doc_count": 0,
                    "extended_bounds": {"min": "2023-01-01", "max": "2023-12-31"}
                }
            }
        }
    }

def generate_sum_agg_object():
    return {
        "aggs": {
            "total_price": ["sum"]  # ✅ Simplified format: ["aggregation_type"]
        }
    }

def generate_min_agg_object():
    return {
        "aggs": {
            "price": ["min"]  # ✅ Simplified format: ["aggregation_type"]
        }
    }

def generate_max_agg_object():
    return {
        "aggs": {
            "price": ["max"]  # ✅ Simplified format: ["aggregation_type"]
        }
    }

def generate_cardinality_agg_object():
    return {
        "aggs": {
            "unique_users": ["cardinality", 3000]  # ✅ ["AggregationType", precision_threshold]
        }
    }

def generate_composite_agg_object():
    return {
        "aggs": {
            "composite_example": [
                "composite",
                {
                    "sources": [
                        {"name": "category_terms", "terms": {"field": "category"}},
                        {"name": "price_histogram", "histogram": {"field": "price", "interval": 50}}
                    ],
                    "size": 20,
                    "order": {"category_terms": "asc", "price_histogram": "desc"},
                    "after": {"category": "some_category", "price": 100}
                }
            ]
        }
    }
