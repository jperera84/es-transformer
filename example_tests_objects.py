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
    return [
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
