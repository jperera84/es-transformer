class TermFilter:
    def __init__(self, field, value, boost=None):  # boost is now optional, default is None
        self.field = field
        self.value = value
        self.boost = boost

    def to_elasticsearch(self):
        term_query = {"term": {self.field: self.value}}
        if self.boost is not None:  # Check if boost is provided
            term_query["term"][self.field] = {"value": self.value, "boost": self.boost}
        return term_query

    def to_json(self):
        json_data = {"type": "term", "field": self.field, "value": self.value}
        if self.boost is not None:
            json_data["boost"] = self.boost
        return json_data

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data["value"], data.get("boost"))  # get boost from json

class RangeFilter:
    def __init__(self, field, operator, value):
        self.field = field
        setattr(self, operator, value) # Dynamically set the operator (gt, lt, etc.) as an attribute
        self.operator = operator # Keep track of the initial operator

    def to_elasticsearch(self):
        range_query = {"range": {self.field: {}}}
        for attr, value in self.__dict__.items():
            if attr not in ("field", "operator"): # Exclude field and operator
                range_query["range"][self.field][attr] = value
        return range_query
    
    @property
    def value(self):
        return getattr(self, self.operator) # returns the value of the initial operator

    def to_json(self):
        json_data = {"type": "range", "field": self.field}
        for attr, value in self.__dict__.items():
            if attr not in ("field", "operator"): # Exclude field and operator
                json_data[attr] = value
        return json_data

    @classmethod
    def from_json(cls, data):
        field = data["field"]
        range_filter = cls(field, "gt", None)  # Initialize with a default operator (e.g., "gt") and None value
        for key, value in data.items():
            if key not in ("type", "field"):  # Set all other attributes (gt, lt, etc.)
                setattr(range_filter, key, value)
        return range_filter

class TermsFilter:
    def __init__(self, field, terms):
        self.field = field
        if isinstance(terms, list):
          self.terms = terms
        else:
          self.terms = [terms] # Terms expects a list

    def to_elasticsearch(self):
        return {"terms": {self.field: self.terms}}

    def to_json(self):
        return {"type": "terms", "field": self.field, "terms": self.terms} # Corrected key to "terms"

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data["terms"]) # Corrected key to "terms"
    
class WildcardFilter:  # New class for wildcard queries
    def __init__(self, field, value, boost=None):  # Added boost parameter to __init__
        self.field = field
        self.value = value
        self.boost = boost

    def to_elasticsearch(self):
        wildcard_query = {"wildcard": {self.field: self.value}}
        if self.boost is not None:  # Check if boost is provided
            wildcard_query["wildcard"][self.field] = {"value": self.value, "boost": self.boost}
        return wildcard_query

    def to_json(self):
        json_data = {"type": "wildcard", "field": self.field, "value": self.value}
        if self.boost is not None:
            json_data["boost"] = self.boost
        return json_data

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data["value"], data.get("boost"))  # Use data.get("boost")
    
class BoolFilter:  # New class for boolean logic
    def __init__(self, clause, filters, minimum_should_match=None):
        self.clause = clause  # "must", "must_not", or "should"
        self.filters = filters
        self.minimum_should_match = minimum_should_match
        self.must = []
        self.must_not = []
        self.should = []

        if clause == "must_not":
            self.must_not = filters
        elif clause == "should":
            self.should = filters
        else:
            self.must = filters

    def to_elasticsearch(self):
        bool_query = {"bool": {}}
        if self.must:
            bool_query["bool"]["must"] = [f.to_elasticsearch() for f in self.must]
        if self.must_not:
            bool_query["bool"]["must_not"] = [f.to_elasticsearch() for f in self.must_not]
        if self.should:
            bool_query["bool"]["should"] = [f.to_elasticsearch() for f in self.should]
            if self.minimum_should_match is not None:
                bool_query["bool"]["minimum_should_match"] = self.minimum_should_match
        return bool_query

    def to_json(self):
        json_data = {"type": "bool"}
        if self.must:
            json_data["must"] = [f.to_json() for f in self.must]
        if self.must_not:
            json_data["must_not"] = [f.to_json() for f in self.must_not]
        if self.should:
            json_data["should"] = [f.to_json() for f in self.should]
            if self.minimum_should_match is not None:
                json_data["minimum_should_match"] = self.minimum_should_match
        return json_data

    @classmethod
    def from_json(cls, data):
        clause = None
        filters = None
        minimum_should_match = data.get("minimum_should_match")
        must = data.get("must", [])
        must_not = data.get("must_not", [])
        should = data.get("should", [])

        if must:
          clause = "must"
          filters = [globals()[item["type"].capitalize() + "Filter"].from_json(item) for item in must]
        elif must_not:
          clause = "must_not"
          filters = [globals()[item["type"].capitalize() + "Filter"].from_json(item) for item in must_not]
        elif should:
          clause = "should"
          filters = [globals()[item["type"].capitalize() + "Filter"].from_json(item) for item in should]

        bool_filter = cls(clause, filters, minimum_should_match)
        bool_filter.must = [globals()[item["type"].capitalize() + "Filter"].from_json(item) for item in must if must]
        bool_filter.must_not = [globals()[item["type"].capitalize() + "Filter"].from_json(item) for item in must_not if must_not]
        bool_filter.should = [globals()[item["type"].capitalize() + "Filter"].from_json(item) for item in should if should]

        return bool_filter
    
class MatchFilter:  # New class for match queries
    def __init__(self, field, query, analyzer=None, boost=None, fuzziness=None, operator=None):
        self.field = field
        self.query = query
        self.analyzer = analyzer
        self.boost = boost
        self.fuzziness = fuzziness
        self.operator = operator

    def to_elasticsearch(self):
        match_query = {"match": {self.field: { "query": self.query }}} # Correct structure
        if self.analyzer:
            match_query["match"][self.field]["analyzer"] = self.analyzer
        if self.boost:
            match_query["match"][self.field]["boost"] = self.boost
        if self.fuzziness:
            match_query["match"][self.field]["fuzziness"] = self.fuzziness
        if self.operator:
            match_query["match"][self.field]["operator"] = self.operator
        return match_query

    def to_json(self):
        json_data = {"type": "match", "field": self.field, "query": self.query}
        if self.analyzer:
            json_data["analyzer"] = self.analyzer
        if self.boost:
            json_data["boost"] = self.boost
        if self.fuzziness:
            json_data["fuzziness"] = self.fuzziness
        if self.operator:
            json_data["operator"] = self.operator
        return json_data

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data["query"], data.get("analyzer"), data.get("boost"), data.get("fuzziness"), data.get("operator"))
    
class IdsFilter:  # New class for ids queries
    def __init__(self, values, type=None):
        self.values = values
        self.type = type

    def to_elasticsearch(self):
        ids_query = {"ids": {"values": self.values}}
        if self.type:
            ids_query["ids"]["type"] = self.type
        return ids_query

    def to_json(self):
        json_data = {"type": "ids", "values": self.values}
        if self.type:
            json_data["type_name"] = self.type # Corrected key to "type_name"
        return json_data

    @classmethod
    def from_json(cls, data):
        return cls(data["values"], data.get("type_name")) # Corrected key to "type_name"

class MultiMatchFilter:
    def __init__(self, query, fields, type=None, analyzer=None, boost=None, fuzziness=None, operator=None, cutoff_frequency=None, fuzziness_prefix_length=None, max_expansions=None, minimum_should_match=None, tie_breaker=None):
        self.query = query
        self.fields = fields
        self.type = type
        self.analyzer = analyzer
        self.boost = boost
        self.fuzziness = fuzziness
        self.operator = operator
        self.cutoff_frequency = cutoff_frequency
        self.fuzziness_prefix_length = fuzziness_prefix_length
        self.max_expansions = max_expansions
        self.minimum_should_match = minimum_should_match
        self.tie_breaker = tie_breaker

    def to_elasticsearch(self):
        multi_match_query = {"multi_match": {"query": self.query, "fields": self.fields}}
        if self.type:
            multi_match_query["multi_match"]["type"] = self.type
        if self.analyzer:
            multi_match_query["multi_match"]["analyzer"] = self.analyzer
        if self.boost:
            multi_match_query["multi_match"]["boost"] = self.boost
        if self.fuzziness:
            multi_match_query["multi_match"]["fuzziness"] = self.fuzziness
        if self.operator:
            multi_match_query["multi_match"]["operator"] = self.operator
        if self.cutoff_frequency:
            multi_match_query["multi_match"]["cutoff_frequency"] = self.cutoff_frequency
        if self.fuzziness_prefix_length:
            multi_match_query["multi_match"]["fuzziness_prefix_length"] = self.fuzziness_prefix_length
        if self.max_expansions:
            multi_match_query["multi_match"]["max_expansions"] = self.max_expansions
        if self.minimum_should_match:
            multi_match_query["multi_match"]["minimum_should_match"] = self.minimum_should_match
        if self.tie_breaker:
            multi_match_query["multi_match"]["tie_breaker"] = self.tie_breaker
        return multi_match_query

    def to_json(self):
        json_data = {"type": "multi_match", "query": self.query, "fields": self.fields}
        if self.type:
            json_data["type_name"] = self.type  # Corrected key to "type_name"
        if self.analyzer:
            json_data["analyzer"] = self.analyzer
        if self.boost:
            json_data["boost"] = self.boost
        if self.fuzziness:
            json_data["fuzziness"] = self.fuzziness
        if self.operator:
            json_data["operator"] = self.operator
        if self.cutoff_frequency:
            json_data["cutoff_frequency"] = self.cutoff_frequency
        if self.fuzziness_prefix_length:
            json_data["fuzziness_prefix_length"] = self.fuzziness_prefix_length
        if self.max_expansions:
            json_data["max_expansions"] = self.max_expansions
        if self.minimum_should_match:
            json_data["minimum_should_match"] = self.minimum_should_match
        if self.tie_breaker:
            json_data["tie_breaker"] = self.tie_breaker
        return json_data

    @classmethod
    def from_json(cls, data):
        return cls(
            data["query"],
            data["fields"],
            data.get("type_name"), # Corrected key to "type_name"
            data.get("analyzer"),
            data.get("boost"),
            data.get("fuzziness"),
            data.get("operator"),
            data.get("cutoff_frequency"),
            data.get("fuzziness_prefix_length"),
            data.get("max_expansions"),
            data.get("minimum_should_match"),
            data.get("tie_breaker"),
        )

class MatchPhraseFilter:
    def __init__(self, field, query, analyzer=None, boost=None, slop=None):
        self.field = field
        self.query = query
        self.analyzer = analyzer
        self.boost = boost
        self.slop = slop

    def to_elasticsearch(self):
        match_phrase_query = {"match_phrase": {self.field: self.query}} # Corrected line
        if self.analyzer or self.boost or self.slop:  # Only add the nested structure if other parameters are present
            match_phrase_query["match_phrase"][self.field] = {"query": self.query}
            if self.analyzer:
                match_phrase_query["match_phrase"][self.field]["analyzer"] = self.analyzer
            if self.boost:
                match_phrase_query["match_phrase"][self.field]["boost"] = self.boost
            if self.slop:
                match_phrase_query["match_phrase"][self.field]["slop"] = self.slop
        return match_phrase_query

    def to_json(self):
        json_data = {"type": "match_phrase", "field": self.field, "query": self.query}
        if self.analyzer:
            json_data["analyzer"] = self.analyzer
        if self.boost:
            json_data["boost"] = self.boost
        if self.slop:
            json_data["slop"] = self.slop
        return json_data

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data["query"], data.get("analyzer"), data.get("boost"), data.get("slop"))

class QueryStringFilter:
    def __init__(self, query, default_field=None, analyzer=None, boost=None, default_operator=None, allow_leading_wildcard=None, lowercase_expanded_terms=None, enable_position_increments=None, fuzziness=None, fuzzy_max_expansions=None, fuzzy_prefix_length=None, lenient=None, max_determinized_states=None, minimum_should_match=None, phrase_slop=None, quote_analyzer=None, rewrite=None, tie_breaker=None, fields=None): # Added fields parameter
        self.query = query
        self.default_field = default_field
        self.analyzer = analyzer
        self.boost = boost
        self.default_operator = default_operator
        self.allow_leading_wildcard = allow_leading_wildcard
        self.lowercase_expanded_terms = lowercase_expanded_terms
        self.enable_position_increments = enable_position_increments
        self.fuzziness = fuzziness
        self.fuzzy_max_expansions = fuzzy_max_expansions
        self.fuzzy_prefix_length = fuzzy_prefix_length
        self.lenient = lenient
        self.max_determinized_states = max_determinized_states
        self.minimum_should_match = minimum_should_match
        self.phrase_slop = phrase_slop
        self.quote_analyzer = quote_analyzer
        self.rewrite = rewrite
        self.tie_breaker = tie_breaker
        self.fields = fields # Added fields attribute

    def to_elasticsearch(self):
        query_string_query = {"query_string": {"query": self.query}}
        if self.default_field:
            query_string_query["query_string"]["default_field"] = self.default_field
        if self.analyzer:
            query_string_query["query_string"]["analyzer"] = self.analyzer
        if self.boost:
            query_string_query["query_string"]["boost"] = self.boost
        if self.default_operator:
            query_string_query["query_string"]["default_operator"] = self.default_operator
        if self.allow_leading_wildcard:
            query_string_query["query_string"]["allow_leading_wildcard"] = self.allow_leading_wildcard
        if self.lowercase_expanded_terms:
            query_string_query["query_string"]["lowercase_expanded_terms"] = self.lowercase_expanded_terms
        if self.enable_position_increments:
            query_string_query["query_string"]["enable_position_increments"] = self.enable_position_increments
        if self.fuzziness:
            query_string_query["query_string"]["fuzziness"] = self.fuzziness
        if self.fuzzy_max_expansions:
            query_string_query["query_string"]["fuzzy_max_expansions"] = self.fuzzy_max_expansions
        if self.fuzzy_prefix_length:
            query_string_query["query_string"]["fuzzy_prefix_length"] = self.fuzzy_prefix_length
        if self.lenient:
            query_string_query["query_string"]["lenient"] = self.lenient
        if self.max_determinized_states:
            query_string_query["query_string"]["max_determinized_states"] = self.max_determinized_states
        if self.minimum_should_match:
            query_string_query["query_string"]["minimum_should_match"] = self.minimum_should_match
        if self.phrase_slop:
            query_string_query["query_string"]["phrase_slop"] = self.phrase_slop
        if self.quote_analyzer:
            query_string_query["query_string"]["quote_analyzer"] = self.quote_analyzer
        if self.rewrite:
            query_string_query["query_string"]["rewrite"] = self.rewrite
        if self.tie_breaker:
            query_string_query["query_string"]["tie_breaker"] = self.tie_breaker
        if self.fields: # Added condition for fields
            query_string_query["query_string"]["fields"] = self.fields
        return query_string_query

    def to_json(self):
        """Converts the QueryStringFilter object to a JSON-serializable dictionary."""
        json_data = {
            "type": "query_string",  # Added the "type" field
            "query": self.query,
            "default_field": self.default_field,
            "analyzer": self.analyzer,
            "boost": self.boost,
            "default_operator": self.default_operator,
            "allow_leading_wildcard": self.allow_leading_wildcard,
            "lowercase_expanded_terms": self.lowercase_expanded_terms,
            "enable_position_increments": self.enable_position_increments,
            "fuzziness": self.fuzziness,
            "fuzzy_max_expansions": self.fuzzy_max_expansions,
            "fuzzy_prefix_length": self.fuzzy_prefix_length,
            "lenient": self.lenient,
            "max_determinized_states": self.max_determinized_states,
            "minimum_should_match": self.minimum_should_match,
            "phrase_slop": self.phrase_slop,
            "quote_analyzer": self.quote_analyzer,
            "rewrite": self.rewrite,
            "tie_breaker": self.tie_breaker,
            "fields": self.fields
        }
        # Remove None values for cleaner JSON
        cleaned_data = {k: v for k, v in json_data.items() if v is not None}
        return cleaned_data

    @classmethod
    def from_json(cls, json_data):
        """Creates a QueryStringFilter object from a JSON-serializable dictionary."""
        return cls(
            json_data.get("query"),
            json_data.get("default_field"),
            json_data.get("analyzer"),
            json_data.get("boost"),
            json_data.get("default_operator"),
            json_data.get("allow_leading_wildcard"),
            json_data.get("lowercase_expanded_terms"),
            json_data.get("enable_position_increments"),
            json_data.get("fuzziness"),
            json_data.get("fuzzy_max_expansions"),
            json_data.get("fuzzy_prefix_length"),
            json_data.get("lenient"),
            json_data.get("max_determinized_states"),
            json_data.get("minimum_should_match"),
            json_data.get("phrase_slop"),
            json_data.get("quote_analyzer"),
            json_data.get("rewrite"),
            json_data.get("tie_breaker"),
            json_data.get("fields")
        )

def create_filter_object(filter_data):
    """Recursively creates filter objects from the provided filter data."""
    filter_objects = []
    if isinstance(filter_data, list):  # AND condition
        for fd in filter_data:
            filter_objects.extend(create_filter_object(fd))  # Recursive call
        return [BoolFilter("must", filter_objects)]

    elif isinstance(filter_data, dict):
        for field, conditions in filter_data.items():
            if field == "ids" and "values" in conditions:
                filter_objects.append(IdsFilter(conditions["values"], conditions.get("type")))
            elif isinstance(conditions, dict):
                if "minimum_should_match" in conditions:  # OR with minimum_should_match
                    or_filters = []
                    minimum_should_match = conditions.pop("minimum_should_match")
                    for operator, value in conditions.items():
                        if operator in ["term", "terms", "gt", "lt", "gte", "lte", "wildcard"]:
                            or_filters.extend(create_filter_object({field: {operator: value}}))  # Recursive
                    filter_objects.append(BoolFilter("should", or_filters, minimum_should_match))
                elif "must_not" in conditions:  # NOT condition
                    must_not_filters = []
                    for not_condition in conditions["must_not"]:
                        must_not_filters.extend(create_filter_object({field: not_condition}))  # Recursive
                    filter_objects.append(BoolFilter("must_not", must_not_filters))
                elif "match" in conditions:  # Match query
                    match_params = conditions.pop("match")
                    if isinstance(match_params, dict):
                        filter_objects.append(MatchFilter(field, match_params.pop("query"), match_params.get("analyzer"), match_params.get("boost"), match_params.get("fuzziness"), match_params.get("operator")))
                    else:
                        filter_objects.append(MatchFilter(field, match_params))  # simple match
                elif "multi_match" in conditions:  # MultiMatch query - INTEGRATED
                    multi_match_params = conditions.pop("multi_match")
                    if isinstance(multi_match_params, dict):
                        filter_objects.append(MultiMatchFilter(multi_match_params.pop("query"), field.split(","), multi_match_params.get("type"), multi_match_params.get("analyzer"), multi_match_params.get("boost"), multi_match_params.get("fuzziness"), multi_match_params.get("operator"), multi_match_params.get("cutoff_frequency"), multi_match_params.get("fuzziness_prefix_length"), multi_match_params.get("max_expansions"), multi_match_params.get("minimum_should_match"), multi_match_params.get("tie_breaker")))
                    else:
                        filter_objects.append(MultiMatchFilter(multi_match_params, field.split(",")))  # simple multi_match
                elif "match_phrase" in conditions:  # MatchPhrase query - INTEGRATED
                    match_phrase_params = conditions.pop("match_phrase")
                    if isinstance(match_phrase_params, dict):
                        filter_objects.append(MatchPhraseFilter(field, match_phrase_params.pop("query"), match_phrase_params.get("analyzer"), match_phrase_params.get("boost"), match_phrase_params.get("slop")))  # Added slop
                    else:
                        filter_objects.append(MatchPhraseFilter(field, match_phrase_params))  # simple match_phrase
                elif "query_string" in conditions:  # QueryString query
                    query_string_params = conditions.pop("query_string")

                    if isinstance(query_string_params, dict) and "query" in query_string_params: # New format with "query" key
                        query = query_string_params.pop("query")
                        fields = query_string_params.pop("fields", None) # Extract fields and remove it from the dict
                        default_field = query_string_params.pop("default_field", None) # Extract default_field and remove it from the dict

                        allowed_params = ["analyzer", "boost", "default_operator", "allow_leading_wildcard", "lowercase_expanded_terms", "enable_position_increments", "fuzziness", "fuzzy_max_expansions", "fuzzy_prefix_length", "lenient", "max_determinized_states", "minimum_should_match", "phrase_slop", "quote_analyzer", "rewrite", "tie_breaker"]
                        cleaned_params = {k: v for k, v in query_string_params.items() if k in allowed_params}

                        filter_objects.append(QueryStringFilter(query, default_field, fields=fields, **cleaned_params)) # Pass fields

                    elif isinstance(query_string_params, dict): # Old format with parameters directly inside
                        query = query_string_params.pop("query")
                        default_field = query_string_params.pop("default_field", None) # Extract default_field and remove it from the dict

                        allowed_params = ["analyzer", "boost", "default_operator", "allow_leading_wildcard", "lowercase_expanded_terms", "enable_position_increments", "fuzziness", "fuzzy_max_expansions", "fuzzy_prefix_length", "lenient", "max_determinized_states", "minimum_should_match", "phrase_slop", "quote_analyzer", "rewrite", "tie_breaker", "fields"]
                        cleaned_params = {k: v for k, v in query_string_params.items() if k in allowed_params}
                        filter_objects.append(QueryStringFilter(query, default_field, **cleaned_params))

                    else:  # Simple query string (string only)
                        filter_objects.append(QueryStringFilter(query_string_params)) # Only query
                else:  # Range, Term, Terms, Wildcard queries
                    for operator, value in conditions.items():
                        if operator in ["gt", "lt", "gte", "lte"]:
                            filter_objects.append(RangeFilter(field, operator, value))
                        elif operator == "term":
                            filter_objects.append(TermFilter(field, value))
                        elif operator == "terms":
                            filter_objects.append(TermsFilter(field, value))
                        elif operator == "wildcard":
                            filter_objects.append(WildcardFilter(field, value))
                        else:
                            raise ValueError(f"Unsupported operator: {operator}")

            elif isinstance(conditions, list):  # OR conditions or Terms query
                if not (len(conditions) > 0 and isinstance(conditions[-1], dict) and "minimum_should_match" in conditions[-1]):  # Terms query
                    filter_objects.append(TermsFilter(field, conditions))  # Correctly handle single term
                else:  # OR condition
                    or_filters = []
                    minimum_should_match = None

                    if isinstance(conditions[-1], dict) and "minimum_should_match" in conditions[-1]:
                        minimum_should_match = conditions[-1]["minimum_should_match"]
                        conditions = conditions[:-1]

                    for cond in conditions:
                        or_filters.extend(create_filter_object({field: cond}))  # Recursive

                    filter_objects.append(BoolFilter("should", or_filters, minimum_should_match))

            else:  # Term query (single condition)
                filter_objects.append(TermFilter(field, conditions))

        return filter_objects

    else:
        raise TypeError("Filter data must be a list or a dictionary")
    
def build_filter_query_class(filters_data):
    """Builds an Elasticsearch query from filter data (list of dictionaries)."""
    filters = []
    for filter_data in filters_data:
        filters.extend(filter_data) # add all the objects to the filter list
    bool_query = {"bool": {}}
    for filter_obj in filters:  # filters is a list of filter objects
        bool_query["bool"].setdefault("must", []).append(filter_obj.to_elasticsearch())
    return bool_query if bool_query["bool"] else {}