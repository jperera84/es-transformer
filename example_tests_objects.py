def generate_ids_filter_object():
    return {
        "filters": [
            { "ids": ["xxxxxxx", "000000000"] }
        ]
    }

def generate_match_filter_object():
    return {
        "filters": [
            { "title": "quick brown fox" }, # match (full-text search)
            { "title": { "match": "quick brown fox" } }, # match (explicit)
        ]
    }

def generate_range_filter_object():
    return {
        "filters": [
            { "price": { "gt": 10, "lt": 100 } },  # range (numeric field)
            { "price": { "gt": 1, "lt": 9 } }  # range (numeric field)
        ]
    }

def generate_term_filter_object():
    return {
        "filters": [
            { "status": "active" },  # ✅ Inferred as `term`
            { "age": 30 },  # ✅ Inferred as `term`
            { "role": { "term": "Admin" } },  # ✅ Explicit term query
            { "title": "quick brown fox" },  # ✅ Inferred as `match`
            { "price": { "gt": 10, "lt": 100 } }  # ✅ Inferred as `range`
        ]
    }

def generate_terms_filter_object():
    return {
        "filters": [
            { "title": "quick brown fox" },
            { "tags": ["new", "featured"], "boost": 1.0 },
            { "tags": ["electronics", "sale"] },
            { "filename": { "wildcard": "*.log", "boost": 2.0 } }
        ]
    }

def generate_wildcard_filter_object():
    return {
        "filters": [
            { "username": { "wildcard": "user*" } },  # ✅ Inferred as `wildcard`
            { "email": { "wildcard": "*@example.com", "case_insensitive": True } },  # ✅ Case-insensitive wildcard
            { "filename": { "wildcard": "*.log", "boost": 2.0 } }  # ✅ Wildcard with boost
        ]
    }

def generate_bool_filter_object():
    return {
        "filters": [
            [  # AND condition (must)
                {"brand": "Samsung"},
                {
                    "color": [
                        {"term": "black"},
                        {"term": "white"},
                        {"minimum_should_match": 1}
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
