class BaseAggregation:
    def __init__(self, field, name=None, nested_path=None, nested_filter=None, aggs=None):
        self.field = field
        self.name = name
        self.nested_path = nested_path
        self.nested_filter = nested_filter
        self.aggs = aggs or {}

    def _add_nested_clause(self, agg_clause):
        if self.nested_path:
            agg_clause["nested"] = {"path": self.nested_path}
            if self.nested_filter:
                agg_clause["nested"]["filter"] = self.nested_filter
        return agg_clause

    def _add_include_missing(self, agg_clause):
        if hasattr(self, 'include') and self.include is not None:
            agg_clause["include"] = self.include
        if hasattr(self, 'missing') and self.missing is not None:
            agg_clause["missing"] = self.missing
        return agg_clause

class TermsAggregation(BaseAggregation):
    def __init__(self, field, name=None, size=10, order=None, min_doc_count=None, other_bucket=False, include=None, missing=None, nested_path=None, nested_filter=None, aggs=None): # Add aggs parameter
        super().__init__(field, name, nested_path, nested_filter, aggs)  # Pass aggs to super()
        self.size = size
        self.order = order
        self.min_doc_count = min_doc_count
        self.other_bucket = other_bucket
        self.include = include
        self.missing = missing

    def to_elasticsearch(self):
        terms_agg = {"terms": {"field": self.field, "size": self.size}}
        if self.order:
            terms_agg["terms"]["order"] = self.order
        if self.min_doc_count:
            terms_agg["terms"]["min_doc_count"] = self.min_doc_count
        if self.other_bucket:
            terms_agg["terms"]["other_bucket"] = self.other_bucket
        terms_agg = self._add_include_missing(terms_agg)
        terms_agg = self._add_nested_clause(terms_agg)
        if self.aggs:  # Add nested aggregations if present
            terms_agg["aggs"] = build_aggregation_query_class(self.aggs) # Corrected
        return {self.name: terms_agg} if self.name else terms_agg

    def to_json(self):
        return {
            "type": "terms_aggregation",
            "field": self.field,
            "name": self.name,
            "size": self.size,
            "order": self.order,
            "min_doc_count": self.min_doc_count,
            "other_bucket": self.other_bucket,
            "include": self.include,
            "missing": self.missing,
            "nested_path": self.nested_path,
            "nested_filter": self.nested_filter,
        }

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data.get("name"), data.get("size"), data.get("order"), data.get("min_doc_count"),
                   data.get("other_bucket"), data.get("include"), data.get("missing"), data.get("nested_path"),
                   data.get("nested_filter"))

class AvgAggregation(BaseAggregation):
    def __init__(self, field, name=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs) # Correctly pass name to super()

    def to_elasticsearch(self):
        avg_agg = {"avg": {"field": self.field}}
        avg_agg = self._add_nested_clause(avg_agg)
        if self.aggs:  # Add nested aggregations if present
            avg_agg["aggs"] = build_aggregation_query_class(self.aggs) # Corrected

        return {self.name: avg_agg} if self.name else avg_agg

    def to_json(self):
        return {"type": "avg_aggregation", "field": self.field, "name": self.name, "nested_path": self.nested_path,
                "nested_filter": self.nested_filter}

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data.get("name"), data.get("nested_path"), data.get("nested_filter"))

class RangeAggregation(BaseAggregation):
    def __init__(self, field, name=None, ranges=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs)
        self.ranges = ranges or []
        self._validate_ranges()

    def _validate_ranges(self):
        for r in self.ranges:
            if "to" in r and "from" in r and r["to"] <= r["from"]:
                raise ValueError("Invalid range: 'to' must be greater than 'from'")
            keys = list(r.keys())
            if keys.count("to") > 1 or keys.count("from") > 1 or keys.count("key") > 1:
                raise ValueError("Invalid range: Duplicate 'to', 'from', or 'key' keys are not allowed in a single range definition.")

    def to_elasticsearch(self):
        range_agg = {"range": {self.field: {}}}
        for r in self.ranges:
            ordered_r = {}
            if "from" in r:
                ordered_r["from"] = r["from"]
            if "to" in r:
                ordered_r["to"] = r["to"]
            for k,v in r.items(): # Add the rest of the keys
                if k not in ["from", "to"]:
                    ordered_r[k] = v
            range_agg["range"][self.field].update(ordered_r)

        if self.aggs:
            wrapped_aggs = {}
            for name, sub_agg in self.aggs.items():
                elasticsearch_agg = sub_agg.to_elasticsearch() if hasattr(sub_agg, "to_elasticsearch") else sub_agg
                if elasticsearch_agg is not None:  # Check for None result
                    wrapped_aggs[name] = elasticsearch_agg
            range_agg["aggs"] = wrapped_aggs

        if self.nested_path:
            nested_query = {"nested": {"path": self.nested_path}}
            if self.nested_filter:
                nested_query["nested"]["filter"] = self.nested_filter

            # Correct: Wrap the NAMED aggregation, which contains the range and nested aggs
            wrapped_range_agg = {self.name: range_agg} if self.name else range_agg # Correct name wrapping
            nested_query["nested"]["aggs"] = wrapped_range_agg
            return nested_query

        return {self.name: range_agg} if self.name else range_agg # Correct name wrapping

    def to_json(self):
        return {"type": "range_aggregation", "field": self.field, "name": self.name, "ranges": self.ranges,
                "nested_path": self.nested_path, "nested_filter": self.nested_filter}

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data.get("name"), data.get("ranges"), data.get("nested_path"),
                   data.get("nested_filter"))

class HistogramAggregation(BaseAggregation):
    def __init__(self, field, name=None, interval=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs)
        self.interval = interval

    def to_elasticsearch(self):
        histogram_agg = {"histogram": {"field": self.field, "interval": self.interval}}
        histogram_agg = self._add_nested_clause(histogram_agg)
        if self.aggs:  # Add nested aggregations if present
            histogram_agg["aggs"] = build_aggregation_query_class(self.aggs) # Corrected
        return {self.name: histogram_agg} if self.name else histogram_agg

    def to_json(self):
        return {"type": "histogram_aggregation", "field": self.field, "name": self.name, "interval": self.interval,
                "nested_path": self.nested_path, "nested_filter": self.nested_filter}

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data.get("name"), data.get("interval"), data.get("nested_path"),
                   data.get("nested_filter"))

class DateHistogramAggregation(BaseAggregation):
    def __init__(self, field, name=None, interval=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs)
        self.interval = interval

    def to_elasticsearch(self):
        date_histogram_agg = {"date_histogram": {"field": self.field, "interval": self.interval}}
        date_histogram_agg = self._add_nested_clause(date_histogram_agg)
        if self.aggs:  # Add nested aggregations if present
            date_histogram_agg["aggs"] = build_aggregation_query_class(self.aggs) # Corrected
        return {self.name: date_histogram_agg} if self.name else date_histogram_agg


    def to_json(self):
        return {"type": "date_histogram_aggregation", "field": self.field, "name": self.name, "interval": self.interval,
                "nested_path": self.nested_path, "nested_filter": self.nested_filter}

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data.get("name"), data.get("interval"), data.get("nested_path"),
                   data.get("nested_filter"))

class SumAggregation(BaseAggregation):
    def __init__(self, field, name=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs)

    def to_elasticsearch(self):
        sum_agg = {"sum": {"field": self.field}}
        sum_agg = self._add_nested_clause(sum_agg)
        if self.aggs:  # Add nested aggregations if present
            sum_agg["aggs"] = build_aggregation_query_class(self.aggs) # Corrected
        return {self.name: sum_agg} if self.name else sum_agg

    def to_json(self):
        return {"type": "sum_aggregation", "field": self.field, "name": self.name, "nested_path": self.nested_path,
                "nested_filter": self.nested_filter}

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data.get("name"), data.get("nested_path"), data.get("nested_filter"))
 
class MinAggregation(BaseAggregation):
    def __init__(self, field, name=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs)

    def to_elasticsearch(self):
        min_agg = {"min": {"field": self.field}}
        min_agg = self._add_nested_clause(min_agg)
        if self.aggs:  # Add nested aggregations if present
            min_agg["aggs"] = build_aggregation_query_class(self.aggs) # Corrected
        return {self.name: min_agg} if self.name else min_agg


    def to_json(self):
        return {"type": "min_aggregation", "field": self.field, "nested_path": self.nested_path, "nested_filter": self.nested_filter}

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data.get("nested_path"), data.get("nested_filter"))

class MaxAggregation(BaseAggregation):
    def __init__(self, field, name=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs)

    def to_elasticsearch(self):
        max_agg = {"max": {"field": self.field}}
        max_agg = self._add_nested_clause(max_agg)
        if self.aggs:  # Add nested aggregations if present
            max_agg["aggs"] = build_aggregation_query_class(self.aggs) # Corrected
        return {self.name: max_agg} if self.name else max_agg

    def to_json(self):
        return {"type": "max_aggregation", "field": self.field, "nested_path": self.nested_path, "nested_filter": self.nested_filter}

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data.get("nested_path"), data.get("nested_filter"))

class CardinalityAggregation(BaseAggregation):
    def __init__(self, field, name=None, precision_threshold=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs)
        self.precision_threshold = precision_threshold

    def to_elasticsearch(self):
        cardinality_agg = {"cardinality": {"field": self.field}}
        if self.precision_threshold is not None:
            cardinality_agg["cardinality"]["precision_threshold"] = self.precision_threshold
        return {self.name: self._add_nested_clause(cardinality_agg)} if self.name else self._add_nested_clause(cardinality_agg)

    def to_json(self):
        return {
            "type": "cardinality_aggregation",
            "field": self.field,
            "name": self.name,
            "precision_threshold": self.precision_threshold,
            "nested_path": self.nested_path,
            "nested_filter": self.nested_filter,
            "aggs": self.aggs,
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            data["field"],
            data.get("name"),
            data.get("precision_threshold"),
            data.get("nested_path"),
            data.get("nested_filter"),
            data.get("aggs"),
        )

class CompositeAggregation(BaseAggregation):
    def __init__(self, name=None, sources=None, size=10, after=None, order=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(None, name, nested_path, nested_filter, aggs)
        self.sources = sources or []
        self.size = size
        self.after = after
        self.order = order  # Add order parameter

    def to_elasticsearch(self):
        composite_agg = {"composite": {"sources": self.sources, "size": self.size}}
        if self.after:
            composite_agg["composite"]["after"] = self.after

        if self.order:
            composite_agg["composite"]["order"] = self.order  # Use the dictionary directly

        return {self.name: self._add_nested_clause(composite_agg)} if self.name else self._add_nested_clause(composite_agg)


    def to_json(self):
        return {
            "type": "composite_aggregation",
            "name": self.name,
            "sources": self.sources,
            "size": self.size,
            "after": self.after,
            "order": self.order,  # Add order to JSON
            "nested_path": self.nested_path,
            "nested_filter": self.nested_filter,
            "aggs": self.aggs,
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            data.get("name"),
            data.get("sources"),
            data.get("size"),
            data.get("after"),
            data.get("order"),  # Add order to from_json
            data.get("nested_path"),
            data.get("nested_filter"),
            data.get("aggs"),
        )

def create_single_aggregation_object(agg_def, name):
    if isinstance(agg_def, dict):
        if "terms" in agg_def:
            aggs = agg_def["terms"].get("aggs")  # Get nested aggs
            terms_agg = TermsAggregation(
                field=agg_def["terms"]["field"],
                name=name,
                size=agg_def["terms"].get("size"),
                order=agg_def["terms"].get("order"),
                min_doc_count=agg_def["terms"].get("min_doc_count"),
                other_bucket=agg_def["terms"].get("other_bucket"),
                include=agg_def["terms"].get("include"),
                missing=agg_def["terms"].get("missing"),
                nested_path=agg_def.get("nested_path"),
                nested_filter=agg_def.get("nested_filter"),
                aggs=aggs,  # Add nested aggs
            )
            return terms_agg
        elif "avg" in agg_def:
            aggs = agg_def["avg"].get("aggs")  # Get nested aggs
            avg_agg = AvgAggregation(
                field=agg_def["avg"]["field"],
                name=name,
                nested_path=agg_def.get("nested_path"),
                nested_filter=agg_def.get("nested_filter"),
                aggs=aggs,  # Add nested aggs
            )
            return avg_agg
        elif "range" in agg_def:
            aggs = agg_def["range"].get("aggs")  # Get nested aggs
            range_agg = RangeAggregation(
                field=agg_def["range"]["field"],
                name=name,
                ranges=agg_def["range"].get("ranges"),
                nested_path=agg_def.get("nested_path"),
                nested_filter=agg_def.get("nested_filter"),
                aggs=aggs,  # Add nested aggs
            )
            return range_agg
        elif "histogram" in agg_def:
            aggs = agg_def["histogram"].get("aggs")  # Get nested aggs
            histogram_agg = HistogramAggregation(
                field=agg_def["histogram"]["field"],
                name=name,
                interval=agg_def["histogram"].get("interval"),
                nested_path=agg_def.get("nested_path"),
                nested_filter=agg_def.get("nested_filter"),
                aggs=aggs,  # Add nested aggs
            )
            return histogram_agg
        elif "date_histogram" in agg_def:
            aggs = agg_def["date_histogram"].get("aggs")  # Get nested aggs
            date_histogram_agg = DateHistogramAggregation(
                field=agg_def["date_histogram"]["field"],
                name=name,
                interval=agg_def["date_histogram"].get("interval"),
                nested_path=agg_def.get("nested_path"),
                nested_filter=agg_def.get("nested_filter"),
                aggs=aggs,  # Add nested aggs
            )
            return date_histogram_agg
        elif "sum" in agg_def:
            aggs = agg_def["sum"].get("aggs")  # Get nested aggs
            sum_agg = SumAggregation(
                field=agg_def["sum"]["field"],
                name=name,
                nested_path=agg_def.get("nested_path"),
                nested_filter=agg_def.get("nested_filter"),
                aggs=aggs,  # Add nested aggs
            )
            return sum_agg
        elif "min" in agg_def:
            aggs = agg_def["min"].get("aggs")  # Get nested aggs
            min_agg = MinAggregation(
                field=agg_def["min"]["field"],
                name=name,
                nested_path=agg_def.get("nested_path"),
                nested_filter=agg_def.get("nested_filter"),
                aggs=aggs,  # Add nested aggs
            )
            return min_agg
        elif "max" in agg_def:
            aggs = agg_def["max"].get("aggs")  # Get nested aggs
            max_agg = MaxAggregation(
                field=agg_def["max"]["field"],
                name=name,
                nested_path=agg_def.get("nested_path"),
                nested_filter=agg_def.get("nested_filter"),
                aggs=aggs,  # Add nested aggs
            )
            return max_agg
        elif "cardinality" in agg_def:  # Add cardinality aggregation
            aggs = agg_def["cardinality"].get("aggs")
            cardinality_agg = CardinalityAggregation(
                field=agg_def["cardinality"]["field"],
                name=name,
                precision_threshold=agg_def["cardinality"].get("precision_threshold"),
                nested_path=agg_def.get("nested_path"),
                nested_filter=agg_def.get("nested_filter"),
                aggs=aggs,
            )
            return cardinality_agg
        elif "composite" in agg_def:
            aggs = agg_def["composite"].get("aggs")
            composite_agg = CompositeAggregation(
                name=name,
                sources=agg_def["composite"]["sources"],
                size=agg_def["composite"].get("size"),
                after=agg_def["composite"].get("after"),
                nested_path=agg_def.get("nested_path"),
                nested_filter=agg_def.get("nested_filter"),
                order=agg_def["composite"].get("order"),  # Add order to CompositeAggregation
                aggs=aggs,
            )
            return composite_agg
        else:
            raise ValueError(f"Unsupported aggregation type: {agg_def.keys()}")
    elif isinstance(agg_def, BaseAggregation):
        return agg_def
    else:
        raise TypeError("Invalid aggregation definition. Must be a dictionary or a BaseAggregation instance.")

def create_aggregation_object(agg_data):
    agg_objects = {}  # Use a dictionary to store aggregations by name

    if isinstance(agg_data, list):  # Handle a list of aggregations
        for agg in agg_data:
            if isinstance(agg, dict):
                for name, agg_def in agg.items():  # Iterate through named aggregations
                    agg_objects[name] = create_single_aggregation_object(agg_def, name)
            elif isinstance(agg, BaseAggregation): # if is already a BaseAggregation object just add it
                agg_objects[agg.name] = agg
            else:
                raise TypeError("Aggregation data must be a list of dictionaries or BaseAggregation objects")

    elif isinstance(agg_data, dict):  # Handle a dictionary of aggregations
        for name, agg_def in agg_data.items():
            agg_objects[name] = create_single_aggregation_object(agg_def, name)

    elif isinstance(agg_data, BaseAggregation): # if is already a BaseAggregation object just add it
        agg_objects[agg_data.name] = agg_data

    else:
        raise TypeError("Aggregation data must be a list or a dictionary or a BaseAggregation object")

    return agg_objects

def build_aggregation_query_class(aggs_data):
    agg_objects = create_aggregation_object(aggs_data)
    aggs_query = {}
    for name, agg_obj in agg_objects.items():
        aggs_query.update(agg_obj.to_elasticsearch())
    return aggs_query
