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