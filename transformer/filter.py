import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

VALID_OPERATORS = {"OR", "AND", "gt", "lt", "gte", "lte", "term", "terms", "wildcard", "match", "match_phrase", "query_string"}


class IdsFilter:
    def __init__(self, values):
        self.values = values

    def to_elasticsearch(self):
        return {"ids": {"values": self.values}}

    def to_json(self):
        return {"type": "ids", "values": self.values}

    @classmethod
    def from_json(cls, data):
        return cls(data["values"])

class MatchFilter:
    def __init__(self, field, value, analyzer=None):
        self.field = field
        self.value = value
        self.analyzer = analyzer

    def to_elasticsearch(self):
        match_query = {
            "match": {
                self.field: {"query": self.value}
            }
        }
        if self.analyzer:
            match_query["match"][self.field]["analyzer"] = self.analyzer
        return match_query

    def to_json(self):
        json_data = {
            "type": "match",
            "field": self.field,
            "value": self.value
        }
        if self.analyzer:
            json_data["analyzer"] = self.analyzer
        return json_data

    @classmethod
    def from_json(cls, data):
        return cls(
            field=data["field"],
            value=data["value"],
            analyzer=data.get("analyzer")
        )

class RangeFilter:

    def __init__(self, field, **conditions):
        self.field = field
        self.conditions = {}

        # Validate and store only valid range conditions
        for operator, value in conditions.items():
            if operator not in VALID_OPERATORS:
                raise ValueError(f"Invalid range operator '{operator}'. Allowed: {VALID_OPERATORS}")
            self.conditions[operator] = value

    def to_elasticsearch(self):
        """Generates an Elasticsearch range query."""
        return {"range": {self.field: self.conditions}}

    def to_json(self):
        """Converts the filter to a JSON-serializable dictionary."""
        return {"type": "range", "field": self.field, **self.conditions}

    @classmethod
    def from_json(cls, data):
        """Creates a RangeFilter object from a JSON dictionary."""
        field = data.pop("field")  # Extract field name
        return cls(field, **data)  # Pass remaining data as conditions

class TermFilter:
    def __init__(self, field, value, boost=None, case_insensitive=False):
        self.field = field
        self.value = value
        self.boost = boost
        self.case_insensitive = case_insensitive

    def to_elasticsearch(self):
        """Converts TermFilter into an Elasticsearch-compatible term query."""
        term_query = {"term": {self.field: {}}}

        # If no additional properties, avoid unnecessary wrapping
        if self.boost is None and not self.case_insensitive:
            term_query["term"][self.field] = self.value  # ✅ Avoids wrapping in `{"value": ...}`
        else:
            term_query["term"][self.field]["value"] = self.value
            if self.boost is not None:
                term_query["term"][self.field]["boost"] = self.boost
            if self.case_insensitive:
                term_query["term"][self.field]["case_insensitive"] = True

        return term_query

    def to_json(self):
        json_data = {
            "type": "term",
            "field": self.field,
            "value": self.value
        }
        if self.boost is not None:
            json_data["boost"] = self.boost
        if self.case_insensitive:
            json_data["case_insensitive"] = True
        return json_data

    @classmethod
    def from_json(cls, data):
        return cls(
            field=data["field"],
            value=data["value"],
            boost=data.get("boost"),
            case_insensitive=data.get("case_insensitive", False)
        )

class TermsFilter:
    def __init__(self, field, terms, boost=None):
        """
        Initialize a TermsFilter.

        :param field: The field to search.
        :param terms: A list of exact terms to match.
        :param boost: (Optional) Boost value to increase or decrease relevance.
        """
        self.field = field
        if isinstance(terms, list):
            self.terms = terms
        else:
            self.terms = [terms]  # Ensure terms is a list
        self.boost = boost

    def to_elasticsearch(self):
        """
        Convert the TermsFilter to an Elasticsearch-compatible query.

        :return: A dictionary representing the terms query.
        """
        terms_query = {"terms": {self.field: self.terms}}
        if self.boost is not None:
            terms_query["terms"]["boost"] = self.boost
        return terms_query

    def to_json(self):
        """
        Convert the TermsFilter to a JSON-serializable dictionary.

        :return: A dictionary representation of the TermsFilter.
        """
        json_data = {
            "type": "terms",
            "field": self.field,
            "terms": self.terms
        }
        if self.boost is not None:
            json_data["boost"] = self.boost
        return json_data

    @classmethod
    def from_json(cls, data):
        """
        Create a TermsFilter instance from a JSON dictionary.

        :param data: A dictionary containing the TermsFilter data.
        :return: An instance of TermsFilter.
        """
        return cls(
            data["field"],
            data["terms"],
            data.get("boost")
        )

class WildcardFilter:
    def __init__(self, field, value, boost=None, case_insensitive=False, rewrite=None):
        self.field = field
        self.value = value
        self.boost = boost
        self.case_insensitive = case_insensitive
        self.rewrite = rewrite  # Optional parameter

    def to_elasticsearch(self):
        wildcard_query = {"wildcard": {self.field: {"value": self.value}}}

        if self.case_insensitive:
            wildcard_query["wildcard"][self.field]["case_insensitive"] = True

        if self.rewrite:
            wildcard_query["wildcard"][self.field]["rewrite"] = self.rewrite

        if self.boost is not None:
            return {
                "bool": {
                    "should": [wildcard_query],
                    "minimum_should_match": 1,
                    "boost": self.boost
                }
            }

        return wildcard_query

    def to_json(self):
        json_data = {
            "type": "wildcard",
            "field": self.field,
            "value": self.value
        }
        if self.boost is not None:
            json_data["boost"] = self.boost
        if self.case_insensitive:
            json_data["case_insensitive"] = True
        if self.rewrite:
            json_data["rewrite"] = self.rewrite
        return json_data

    @classmethod
    def from_json(cls, data):
        return cls(
            field=data["field"],
            value=data["value"],
            boost=data.get("boost"),
            case_insensitive=data.get("case_insensitive", False),
            rewrite=data.get("rewrite")
        )

class BoolFilter:
    def __init__(self, must=None, must_not=None, should=None, minimum_should_match=None):
        """
        Initialize a BoolFilter.

        :param must: (Optional) List of queries that must match.
        :param must_not: (Optional) List of queries that must not match.
        :param should: (Optional) List of queries that should match.
        :param minimum_should_match: (Optional) Minimum number of should clauses to match.
        """
        self.must = must or []
        self.must_not = must_not or []
        self.should = should or []
        self.minimum_should_match = minimum_should_match if self.should else None  # Only applies when `should` exists

    def to_elasticsearch(self):
        """
        Convert the BoolFilter to an Elasticsearch-compatible query.

        :return: A dictionary representing the bool query.
        """
        bool_query = {"bool": {}}
        if self.must:
            bool_query["bool"]["must"] = [q.to_elasticsearch() for q in self.must]
        if self.must_not:
            bool_query["bool"]["must_not"] = [q.to_elasticsearch() for q in self.must_not]
        if self.should:
            bool_query["bool"]["should"] = [q.to_elasticsearch() for q in self.should]
        if self.minimum_should_match is not None:
            bool_query["bool"]["minimum_should_match"] = self.minimum_should_match
        return bool_query

    def to_json(self):
        """
        Convert the BoolFilter to a JSON-serializable dictionary.

        :return: A dictionary representation of the BoolFilter.
        """
        json_data = {"type": "bool"}
        if self.must:
            json_data["must"] = [q.to_json() for q in self.must]
        if self.must_not:
            json_data["must_not"] = [q.to_json() for q in self.must_not]
        if self.should:
            json_data["should"] = [q.to_json() for q in self.should]
        if self.minimum_should_match is not None:
            json_data["minimum_should_match"] = self.minimum_should_match
        return json_data

    @classmethod
    def from_json(cls, data):
        """Creates a BoolFilter instance from a JSON dictionary."""

        def load_filters(filters_list):
            """Ensures filters are properly reconstructed based on type hints in JSON."""
            reconstructed_filters = []
            for item in filters_list:
                if "type" in item:  
                    filter_class_name = item["type"].capitalize() + "Filter"
                    if filter_class_name in globals():
                        reconstructed_filters.append(globals()[filter_class_name].from_json(item))
                    else:
                        raise ValueError(f"Unknown filter type: {item['type']}")
                else:
                    # Fallback to `create_filter_object` when type is missing
                    reconstructed_filters.append(create_filter_object(item))
            return reconstructed_filters

        must = load_filters(data.get("must", []))
        must_not = load_filters(data.get("must_not", []))
        should = load_filters(data.get("should", []))
        minimum_should_match = data.get("minimum_should_match")

        return cls(must=must, must_not=must_not, should=should, minimum_should_match=minimum_should_match)

def create_filter_object(filter_data):
    """Recursively converts a simplified data model into Elasticsearch filter objects."""
    
    if isinstance(filter_data, list):  
        # ✅ Handle AND condition (must)
        return BoolFilter(must=[create_filter_object(fd) for fd in filter_data])

    elif isinstance(filter_data, dict):
        for field, value in filter_data.items():
            # ✅ Handle `ids` filter separately
            if field == "ids" and isinstance(value, list):
                return IdsFilter(value)

            elif isinstance(value, list):
                # ✅ Fix: Detect `should` (OR) conditions correctly
                if len(value) > 1 and isinstance(value[-1], dict) and "minimum_should_match" in value[-1]:
                    minimum_should_match = value[-1]["minimum_should_match"]
                    conditions = value[:-1]  # Remove `minimum_should_match` dict from the list
                    
                    return BoolFilter(
                        should=[create_filter_object({field: cond}) for cond in conditions],
                        minimum_should_match=minimum_should_match
                    )
                
                # ✅ Default case: This is a `terms` query
                return TermsFilter(field, value)

            elif isinstance(value, dict):
                # ✅ Handle wildcard filters
                if "wildcard" in value:
                    return WildcardFilter(field, value["wildcard"], boost=value.get("boost"))

                # ✅ Fix: Ensure boost applies only to `terms` queries
                elif "boost" in value and isinstance(value["boost"], (int, float)) and field in value:
                    return BoolFilter(
                        should=[TermsFilter(field, value[field])],
                        minimum_should_match=1
                    )

                elif "match" in value:
                    return MatchFilter(field, value["match"])

                elif "term" in value:
                    return TermFilter(field, value["term"])

                # ✅ Handle range filters properly
                range_operators = {k: v for k, v in value.items() if k in {"gt", "lt", "gte", "lte"}}
                if range_operators:
                    return RangeFilter(field, **range_operators)

                else:
                    raise ValueError(f"Unknown filter structure for field '{field}': {value}")

            else:
                # ✅ Fix: Ensure match vs term is correctly inferred
                if isinstance(value, str) and " " in value:
                    return MatchFilter(field, value)  # Full-text search → match query
                else:
                    return TermFilter(field, value)  # Exact keyword match → term query

    else:
        raise TypeError("Filter data must be a list or a dictionary")

def build_filter_query_class(filters_data):
    """Converts a list of filter objects into an Elasticsearch bool query."""
    if not filters_data:
        return None

    filters = []
    for filter_data in filters_data:
        if isinstance(filter_data, list):  
            filters.extend(filter_data)  # Already a list, extend it normally
        else:
            filters.append(filter_data)  # Wrap single object in a list

    # ✅ If there's only one filter, return it directly (no need for `bool`)
    if len(filters) == 1:
        return filters[0].to_elasticsearch()

    # ✅ Otherwise, wrap multiple filters inside `bool.must`
    return {"bool": {"must": [f.to_elasticsearch() for f in filters]}}

