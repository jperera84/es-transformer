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
    def __init__(self, field, query, analyzer=None, boost=None, fuzziness=None, operator=None, minimum_should_match=None, zero_terms_query=None):
        if not query:
            raise ValueError("MatchFilter requires a non-empty query.")
        if operator and operator not in VALID_OPERATORS:
            raise ValueError(f"Invalid operator '{operator}'. Allowed: {VALID_OPERATORS}")
        if zero_terms_query and zero_terms_query not in {"none", "all"}:
            raise ValueError("zero_terms_query must be either 'none' or 'all'.")

        self.field = field
        self.query = query
        self.analyzer = analyzer
        self.boost = boost
        self.fuzziness = fuzziness
        self.operator = operator
        self.minimum_should_match = minimum_should_match
        self.zero_terms_query = zero_terms_query

    def to_elasticsearch(self):
        match_query = {
            "match": {
                self.field: {
                    "query": self.query
                }
            }
        }
        if self.analyzer:
            match_query["match"][self.field]["analyzer"] = self.analyzer
        if self.boost:
            match_query["match"][self.field]["boost"] = self.boost
        if self.fuzziness:
            match_query["match"][self.field]["fuzziness"] = self.fuzziness
        if self.operator:
            match_query["match"][self.field]["operator"] = self.operator
        if self.minimum_should_match:
            match_query["match"][self.field]["minimum_should_match"] = self.minimum_should_match
        if self.zero_terms_query:
            match_query["match"][self.field]["zero_terms_query"] = self.zero_terms_query

        logger.debug(f"Generated match query: {match_query}")
        return match_query

    def to_json(self):
        json_data = {
            "type": "match",
            "field": self.field,
            "query": self.query
        }
        if self.analyzer:
            json_data["analyzer"] = self.analyzer
        if self.boost:
            json_data["boost"] = self.boost
        if self.fuzziness:
            json_data["fuzziness"] = self.fuzziness
        if self.operator:
            json_data["operator"] = self.operator
        if self.minimum_should_match:
            json_data["minimum_should_match"] = self.minimum_should_match
        if self.zero_terms_query:
            json_data["zero_terms_query"] = self.zero_terms_query
        return json_data

    @classmethod
    def from_json(cls, data):
        return cls(
            data["field"],
            data["query"],
            data.get("analyzer"),
            data.get("boost"),
            data.get("fuzziness"),
            data.get("operator"),
            data.get("minimum_should_match"),
            data.get("zero_terms_query")
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
        """
        Initialize a TermFilter.

        :param field: The field to search.
        :param value: The exact value to match.
        :param boost: (Optional) Boost value to increase or decrease relevance.
        :param case_insensitive: (Optional) Perform case-insensitive matching. Defaults to False.
        """
        self.field = field
        self.value = value
        self.boost = boost
        self.case_insensitive = case_insensitive

    def to_elasticsearch(self):
        """
        Convert the TermFilter to an Elasticsearch-compatible query.

        :return: A dictionary representing the term query.
        """
        term_body = {"value": self.value}
        if self.boost is not None:
            term_body["boost"] = self.boost
        if self.case_insensitive:
            term_body["case_insensitive"] = self.case_insensitive
        return {"term": {self.field: term_body}}

    def to_json(self):
        """
        Convert the TermFilter to a JSON-serializable dictionary.

        :return: A dictionary representation of the TermFilter.
        """
        json_data = {
            "type": "term",
            "field": self.field,
            "value": self.value
        }
        if self.boost is not None:
            json_data["boost"] = self.boost
        if self.case_insensitive:
            json_data["case_insensitive"] = self.case_insensitive
        return json_data

    @classmethod
    def from_json(cls, data):
        """
        Create a TermFilter instance from a JSON dictionary.

        :param data: A dictionary containing the TermFilter data.
        :return: An instance of TermFilter.
        """
        return cls(
            data["field"],
            data["value"],
            data.get("boost"),
            data.get("case_insensitive", False)
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
        """
        Initialize a WildcardFilter.

        :param field: The field to search.
        :param value: The wildcard pattern to match.
        :param boost: (Optional) Boost value to increase or decrease relevance.
        :param case_insensitive: (Optional) Perform case-insensitive matching. Defaults to False.
        :param rewrite: (Optional) Method used to rewrite the query.
        """
        self.field = field
        self.value = value
        self.boost = boost
        self.case_insensitive = case_insensitive
        self.rewrite = rewrite

    def to_elasticsearch(self):
        """
        Convert the WildcardFilter to an Elasticsearch-compatible query.

        :return: A dictionary representing the wildcard query.
        """
        wildcard_body = {"value": self.value}
        if self.boost is not None:
            wildcard_body["boost"] = self.boost
        if self.case_insensitive:
            wildcard_body["case_insensitive"] = self.case_insensitive
        if self.rewrite:
            wildcard_body["rewrite"] = self.rewrite
        return {"wildcard": {self.field: wildcard_body}}

    def to_json(self):
        """
        Convert the WildcardFilter to a JSON-serializable dictionary.

        :return: A dictionary representation of the WildcardFilter.
        """
        json_data = {
            "type": "wildcard",
            "field": self.field,
            "value": self.value
        }
        if self.boost is not None:
            json_data["boost"] = self.boost
        if self.case_insensitive:
            json_data["case_insensitive"] = self.case_insensitive
        if self.rewrite:
            json_data["rewrite"] = self.rewrite
        return json_data

    @classmethod
    def from_json(cls, data):
        """
        Create a WildcardFilter instance from a JSON dictionary.

        :param data: A dictionary containing the WildcardFilter data.
        :return: An instance of WildcardFilter.
        """
        return cls(
            data["field"],
            data["value"],
            data.get("boost"),
            data.get("case_insensitive", False),
            data.get("rewrite")
        )

class BoolFilter:
    def __init__(self, must=None, must_not=None, should=None, filter=None, minimum_should_match=None):
        """
        Initialize a BoolFilter.

        :param must: (Optional) List of queries that must match.
        :param must_not: (Optional) List of queries that must not match.
        :param should: (Optional) List of queries that should match.
        :param filter: (Optional) List of queries to filter results.
        :param minimum_should_match: (Optional) Minimum number of should clauses to match.
        """
        self.must = must or []
        self.must_not = must_not or []
        self.should = should or []
        self.filter = filter or []
        self.minimum_should_match = minimum_should_match

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
        if self.filter:
            bool_query["bool"]["filter"] = [q.to_elasticsearch() for q in self.filter]
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
        if self.filter:
            json_data["filter"] = [q.to_json() for q in self.filter]
        if self.minimum_should_match is not None:
            json_data["minimum_should_match"] = self.minimum_should_match
        return json_data

    @classmethod
    def from_json(cls, data):
        """
        Create a BoolFilter instance from a JSON dictionary.

        :param data: A dictionary containing the BoolFilter data.
        :return: An instance of BoolFilter.
        """
        must = [globals()[item["type"].capitalize() + "Filter"].from_json(item) for item in data.get("must", [])]
        must_not = [globals()[item["type"].capitalize() + "Filter"].from_json(item) for item in data.get("must_not", [])]
        should = [globals()[item["type"].capitalize() + "Filter"].from_json(item) for item in data.get("should", [])]
        filter = [globals()[item["type"].capitalize() + "Filter"].from_json(item) for item in data.get("filter", [])]
        minimum_should_match = data.get("minimum_should_match")
        return cls(must=must, must_not=must_not, should=should, filter=filter, minimum_should_match=minimum_should_match)

def create_filter_object(filter_data):
    """Infers filter type based on structure and converts it to an Elasticsearch query."""
    filter_objects = []

    if isinstance(filter_data, list):  # AND condition
        return [BoolFilter("must", [create_filter_object(fd) for fd in filter_data])]

    elif isinstance(filter_data, dict):
        for field, value in filter_data.items():
            # Handle dictionary values -> Explicit query type (match, term, range, terms, wildcard)
            if isinstance(value, dict):
                if "match" in value:
                    filter_objects.append(MatchFilter(field, value["match"]))
                elif "term" in value:
                    filter_objects.append(TermFilter(field, value["term"]))
                elif "terms" in value:
                    filter_objects.append(TermsFilter(field, value["terms"], value.get("boost")))
                elif "wildcard" in value:
                    filter_objects.append(WildcardFilter(field, value["wildcard"], value.get("boost"), value.get("case_insensitive", False), value.get("rewrite")))
                elif any(op in value for op in ["gt", "lt", "gte", "lte"]):  # Range query
                    filter_objects.append(RangeFilter(field, **value))
                else:
                    raise ValueError(f"Unknown filter structure for field '{field}': {value}")

            # Handle list values -> Assume `terms` query
            elif isinstance(value, list):
                filter_objects.append(TermsFilter(field, value))

            # Handle simple values (string, number, boolean) -> `term` query
            elif isinstance(value, (int, float, bool)):  
                filter_objects.append(TermFilter(field, value))

            elif isinstance(value, str):  
                if " " in value:  # If value contains spaces, assume full-text `match`
                    filter_objects.append(MatchFilter(field, value))
                else:  # Otherwise, assume exact `term`
                    filter_objects.append(TermFilter(field, value))

    return filter_objects

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

    if len(filters) == 1:
        return filters[0].to_elasticsearch()  # Return the single filter directly

    return {"bool": {"must": [f.to_elasticsearch() for f in filters]}}  # Wrap in a `bool` query
