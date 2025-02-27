# Elasticsearch Transformer API - Data Model Documentation

## Overview
The Elasticsearch Transformer API is designed to dynamically generate and execute Elasticsearch queries 
based on a structured yet flexible data model. This document provides a detailed explanation of the data 
model, including filters, sorting, and aggregations.

---

## 1. Filters

Filters are defined as a list or dictionary structure that represents different types of Elasticsearch queries. 

### 1.1 ID Filters
Used to filter documents by their `_id` field.
```json
{
    "filters": [
        { "ids": ["1", "2", "3"] }
    ]
}

1.2 Term Filters

Used for exact matches on keyword fields.

Always show details

{
    "filters": [
        { "event.provider": "pfm" },
        { "trust_initiated": true }
    ]
}

1.3 Match Filters

Used for full-text search.

Always show details

{
    "filters": {
        "formula_metadata.name": ["Threat Detection Rule", "Suspicious Upload Rule"]
    }
}

1.4 Range Filters

Used for numeric and date range queries.

Always show details

{
    "filters": [
        { "@timestamp": { "gte": "2025-01-01T00:00:00.000Z", "lte": "2025-01-02T00:00:00.000Z" } },
        { "action_count": { "gt": 5, "lt": 20 } }
    ]
}

1.5 Wildcard Filters

Used for partial matches with wildcard syntax.

Always show details

{
    "filters": [
        { "event.provider": { "wildcard": "sec*" } },
        { "url.path": { "wildcard": "*.log", "boost": 2.0 } }
    ]
}

1.6 Boolean Filters

Used for complex AND/OR conditions.

Always show details

{
    "filters": [
        [
            { "formula_metadata.name": "Threat Detection Rule" },
            { "formula_metadata.tags.value": ["security", "critical"] }
        ]
    ]
}

2. Sorting

Sorting can be defined to order results based on field values.

Always show details

{
    "sorts": [
        { "formula_metadata.name": "asc" },
        { "@timestamp": "desc" }
    ]
}

3. Aggregations

Aggregations allow for grouping and summarizing data.
3.1 Terms Aggregation (Simple)

Always show details

{
    "aggs": {
        "client_id": ["terms", 50]
    }
}

3.2 Nested Aggregations

Always show details

{
    "aggs": {
        "client_id": {
            "terms": {
                "field": "client_id",
                "size": 10,
                "order": { "_count": "desc" }
            },
            "aggs": {
                "formula_matches_id": {
                    "terms": {
                        "field": "formula_matches_id",
                        "size": 10,
                        "order": { "_count": "desc" }
                    },
                    "aggs": {
                        "http.request.method": {
                            "terms": {
                                "field": "http.request.method",
                                "size": 10,
                                "order": { "_count": "desc" }
                            },
                            "aggs": {
                                "source_address": {
                                    "terms": {
                                        "field": "source_address",
                                        "size": 10,
                                        "order": { "_count": "desc" }
                                    },
                                    "aggs": {
                                        "url.domain": {
                                            "terms": {
                                                "field": "url.domain",
                                                "size": 10,
                                                "order": { "_count": "desc" }
                                            },
                                            "aggs": {
                                                "destination_address": {
                                                    "terms": {
                                                        "field": "destination_address",
                                                        "size": 10,
                                                        "order": { "_count": "desc" }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

4. Example Full Query

Always show details

{
  "query": {
    "bool": {
      "must": [
        { "term": { "event.provider": "pfm" } },
        { "term": { "trust_initiated": true } },
        { "range": { "@timestamp": { "gte": "2025-01-01T00:00:00.000Z", "lte": "2025-01-02T00:00:00.000Z" } } }
      ]
    }
  },
  "aggs": {
    "client_id": {
      "terms": {
        "field": "client_id",
        "size": 10,
        "order": { "_count": "desc" }
      },
      "aggs": {
        "formula_matches_id": {
          "terms": {
            "field": "formula_matches_id",
            "size": 10,
            "order": { "_count": "desc" }
          }
        }
      }
    }
  }
}

5. Summary

This documentation provides a structured format for dynamically generating Elasticsearch queries using the Transformer API. The data model ensures flexibility while keeping the query generation optimized. """
Save the documentation as a markdown file

file_path = "/mnt/data/

elasticsearch_transformer_api_documentation.md" with open(file_path, "w") as doc_file: doc_file.write(documentation_content)

file_path

Always show details