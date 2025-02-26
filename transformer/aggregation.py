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
    def __init__(self, field, size=None, name=None):
        if not isinstance(field, str) or (size is not None and not isinstance(size, int)):
            raise TypeError("Invalid format for TermsAggregation. 'field' must be a string and 'size' must be an integer.")
        
        super().__init__(field, name=name)
        self.size = size

    @classmethod
    def from_json(cls, data):
        """Supports both traditional and simplified JSON models."""
        if isinstance(data, list) and len(data) == 2:  # Supports ["terms", 20] format
            agg_type, size = data
            if agg_type != "terms":
                raise ValueError(f"Invalid aggregation type '{agg_type}'. Expected 'terms'.")
            return cls(field=None, size=size)  # Field will be inferred in processing
        elif isinstance(data, dict) and "terms" in data:
            return cls(field=data["terms"].get("field"), size=data["terms"].get("size"))
        else:
            raise ValueError(f"Invalid format for TermsAggregation: {data}")

    def to_elasticsearch(self):
        """Converts the TermsAggregation object to an Elasticsearch aggregation query."""
        if not self.field:
            raise ValueError("Field must be set for TermsAggregation.")

        agg = {"terms": {"field": self.field}}
        if self.size:
            agg["terms"]["size"] = self.size
        return {self.name: agg}


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

class AvgAggregation(BaseAggregation):
    def __init__(self, field, name=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name if name else None, nested_path, nested_filter, aggs)  # ✅ Only set name if explicitly provided

    @classmethod
    def from_json(cls, data):
        """Supports both traditional and simplified JSON models."""
        if isinstance(data, list) and len(data) == 1:  # Supports ["avg"] format
            agg_type = data[0]
            if agg_type != "avg":
                raise ValueError(f"Invalid aggregation type '{agg_type}'. Expected 'avg'.")
            return cls(field=None, name=None)  # Field will be assigned later

        elif isinstance(data, dict) and "avg" in data:
            field = data["avg"].get("field")
            return cls(field, name=field)  # Ensure name is set to the field name

        else:
            raise ValueError(f"Invalid format for AvgAggregation: {data}")

    def to_elasticsearch(self):
        avg_agg = {"avg": {"field": self.field}}
        avg_agg = self._add_nested_clause(avg_agg)
        
        if self.aggs:  # Add nested aggregations if present
            avg_agg["aggs"] = build_aggregation_query_class(self.aggs)

        return {self.name: avg_agg} if self.name else avg_agg  # ✅ No wrapping when name is None


    def to_json(self):
        return {"type": "avg_aggregation", "field": self.field, "name": self.name, "nested_path": self.nested_path,
                "nested_filter": self.nested_filter}

class RangeAggregation(BaseAggregation):
    def __init__(self, field, name=None, ranges=None, nested_path=None, nested_filter=None, aggs=None):
        if not field:
            raise ValueError("Field must be provided for RangeAggregation.")  # ✅ Ensure error is raised
        
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
        range_agg = {
            "range": {
                "field": self.field,
                "ranges": self.ranges  # ✅ Store ranges as a list instead of overwriting
            }
        }

        # Add nested sub-aggregations if present
        if self.aggs:
            range_agg["aggs"] = {name: sub_agg.to_elasticsearch() for name, sub_agg in self.aggs.items()}

        # Handle Nested Queries
        if self.nested_path:
            nested_query = {"nested": {"path": self.nested_path}}
            if self.nested_filter:
                nested_query["nested"]["filter"] = self.nested_filter
            nested_query["nested"]["aggs"] = {self.name: range_agg} if self.name else range_agg
            return nested_query

        return {self.name: range_agg} if self.name else range_agg  # ✅ Name is correctly handled

    def to_json(self):
        """Converts the aggregation to a JSON-serializable dictionary."""
        return {
            "type": "range_aggregation",
            "field": self.field,
            "name": self.name,
            "ranges": self.ranges,
            **({ "nested_path": self.nested_path } if self.nested_path else {}),
            **({ "nested_filter": self.nested_filter } if self.nested_filter else {})
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            data["field"],
            data.get("name"),
            data.get("ranges"),
            data.get("nested_path"),
            data.get("nested_filter")
        )

class HistogramAggregation(BaseAggregation):
    def __init__(
        self, field, interval, name=None, nested_path=None, nested_filter=None,
        aggs=None, extended_bounds=None, min_doc_count=None, keyed=None
    ):
        super().__init__(field, name, nested_path, nested_filter, aggs)
        self.interval = interval
        self.extended_bounds = extended_bounds
        self.min_doc_count = min_doc_count
        self.keyed = keyed  # New parameter to control dictionary output

    def to_elasticsearch(self):
        histogram_agg = {
            "histogram": {
                "field": self.field,
                "interval": self.interval
            }
        }

        # Add optional parameters if provided
        if self.extended_bounds:
            histogram_agg["histogram"]["extended_bounds"] = self.extended_bounds
        if self.min_doc_count is not None:
            histogram_agg["histogram"]["min_doc_count"] = self.min_doc_count
        if self.keyed is not None:
            histogram_agg["histogram"]["keyed"] = self.keyed

        histogram_agg = self._add_nested_clause(histogram_agg)

        if self.aggs:
            histogram_agg["aggs"] = build_aggregation_query_class(self.aggs)

        return {self.name: histogram_agg} if self.name else histogram_agg

    def to_json(self):
        json_data = {
            "type": "histogram_aggregation",
            "field": self.field,
            "interval": self.interval,
            "name": self.name,
            "nested_path": self.nested_path,
            "nested_filter": self.nested_filter
        }

        # ✅ Only add optional fields if they are not None
        if self.extended_bounds is not None:
            json_data["extended_bounds"] = self.extended_bounds
        if self.min_doc_count is not None:
            json_data["min_doc_count"] = self.min_doc_count
        if self.keyed is not None:
            json_data["keyed"] = self.keyed

        return json_data


    @classmethod
    def from_json(cls, data):
        return cls(
            field=data["field"],
            interval=data["interval"],
            name=data.get("name"),
            nested_path=data.get("nested_path"),
            nested_filter=data.get("nested_filter"),
            extended_bounds=data.get("extended_bounds"),
            min_doc_count=data.get("min_doc_count"),
            keyed=data.get("keyed")
        )

class DateHistogramAggregation(BaseAggregation):
    def __init__(self, field, name=None, interval=None, calendar_interval=None, fixed_interval=None, format=None,
                 time_zone=None, min_doc_count=None, extended_bounds=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs)
        
        # ✅ Ensure only one of these is set
        if interval and (calendar_interval or fixed_interval):
            raise ValueError("Use either 'interval' or 'calendar_interval'/'fixed_interval', not both.")

        self.interval = interval
        self.calendar_interval = calendar_interval
        self.fixed_interval = fixed_interval
        self.format = format
        self.time_zone = time_zone
        self.min_doc_count = min_doc_count
        self.extended_bounds = extended_bounds

    def to_elasticsearch(self):
        """Convert DateHistogramAggregation to an Elasticsearch-compatible format."""
        date_histogram_agg = {
            "date_histogram": {
                "field": self.field
            }
        }

        # ✅ Ensure correct interval usage
        if self.calendar_interval:
            date_histogram_agg["date_histogram"]["calendar_interval"] = self.calendar_interval
        elif self.fixed_interval:
            date_histogram_agg["date_histogram"]["fixed_interval"] = self.fixed_interval
        elif self.interval:
            # Convert `interval` to `calendar_interval` (Elasticsearch doesn't support raw `interval`)
            date_histogram_agg["date_histogram"]["calendar_interval"] = self.interval

        # ✅ Add optional parameters if present
        if self.format:
            date_histogram_agg["date_histogram"]["format"] = self.format
        if self.time_zone:
            date_histogram_agg["date_histogram"]["time_zone"] = self.time_zone
        if self.extended_bounds:
            date_histogram_agg["date_histogram"]["extended_bounds"] = self.extended_bounds

        # ✅ Handle nested aggregation
        date_histogram_agg = self._add_nested_clause(date_histogram_agg)

        # ✅ Add sub-aggregations if they exist
        if self.aggs:
            date_histogram_agg["aggs"] = build_aggregation_query_class(self.aggs)

        # ✅ Ensure correct wrapping of aggregation under field name
        return {self.name: date_histogram_agg} if self.name else {self.field: date_histogram_agg}


    def to_json(self):
        json_data = {
            "type": "date_histogram_aggregation",
            "field": self.field,
            "name": self.name,
            "interval": self.interval,
            "calendar_interval": self.calendar_interval,
            "fixed_interval": self.fixed_interval,
            "format": self.format,
            "time_zone": self.time_zone,
            "min_doc_count": self.min_doc_count,
            "extended_bounds": self.extended_bounds,
            "nested_path": self.nested_path,
            "nested_filter": self.nested_filter
        }

        # ✅ Remove None values
        return {k: v for k, v in json_data.items() if v is not None}

    @classmethod
    def from_json(cls, data):
        return cls(
            field=data["field"],
            name=data.get("name"),
            interval=data.get("interval"),
            calendar_interval=data.get("calendar_interval"),
            fixed_interval=data.get("fixed_interval"),
            format=data.get("format"),
            time_zone=data.get("time_zone"),
            min_doc_count=data.get("min_doc_count"),
            extended_bounds=data.get("extended_bounds"),
            nested_path=data.get("nested_path"),
            nested_filter=data.get("nested_filter")
        )

class SumAggregation(BaseAggregation):
    def __init__(self, field, name=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs)

    def to_elasticsearch(self):
        """Convert SumAggregation to Elasticsearch-compatible format."""
        sum_agg = {"sum": {"field": self.field}}

        # ✅ Handle nested aggregation
        sum_agg = self._add_nested_clause(sum_agg)

        # ✅ Add sub-aggregations if they exist
        if self.aggs:
            sum_agg["aggs"] = build_aggregation_query_class(self.aggs)

        # ✅ Ensure correct wrapping of aggregation under field name
        return {self.name: sum_agg} if self.name else {self.field: sum_agg}

    def to_json(self):
        """Convert SumAggregation to a JSON-serializable format."""
        json_data = {
            "type": "sum_aggregation",
            "field": self.field,
            "name": self.name,
            "nested_path": self.nested_path,
            "nested_filter": self.nested_filter
        }
        # ✅ Remove None values
        return {k: v for k, v in json_data.items() if v is not None}

    @classmethod
    def from_json(cls, data):
        """Reconstruct SumAggregation from JSON."""
        return cls(
            field=data["field"],
            name=data.get("name"),
            nested_path=data.get("nested_path"),
            nested_filter=data.get("nested_filter")
        )

class MinAggregation(BaseAggregation):
    def __init__(self, field, name=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs)

    def to_elasticsearch(self):
        """Convert MinAggregation to an Elasticsearch-compatible format."""
        min_agg = {"min": {"field": self.field}}
        
        # ✅ Handle nested paths/filters if applicable
        min_agg = self._add_nested_clause(min_agg)

        # ✅ Add sub-aggregations if they exist
        if self.aggs:
            min_agg["aggs"] = build_aggregation_query_class(self.aggs)

        # ✅ Ensure correct wrapping of aggregation under field name
        return {self.name: min_agg} if self.name else {self.field: min_agg}

    def to_json(self):
        """Convert MinAggregation to JSON format."""
        json_data = {
            "type": "min_aggregation",
            "field": self.field,
            "name": self.name,
            "nested_path": self.nested_path,
            "nested_filter": self.nested_filter
        }

        # ✅ Remove None values
        return {k: v for k, v in json_data.items() if v is not None}

    @classmethod
    def from_json(cls, data):
        """Deserialize JSON data into MinAggregation object."""
        return cls(
            field=data["field"],
            name=data.get("name"),
            nested_path=data.get("nested_path"),
            nested_filter=data.get("nested_filter")
        )

class MaxAggregation(BaseAggregation):
    def __init__(self, field, name=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs)

    def to_elasticsearch(self):
        """Convert MaxAggregation to an Elasticsearch-compatible format."""
        max_agg = {"max": {"field": self.field}}
        
        # ✅ Handle nested paths/filters if applicable
        max_agg = self._add_nested_clause(max_agg)

        # ✅ Add sub-aggregations if they exist
        if self.aggs:
            max_agg["aggs"] = build_aggregation_query_class(self.aggs)

        # ✅ Ensure correct wrapping of aggregation under field name
        return {self.name: max_agg} if self.name else {self.field: max_agg}

    def to_json(self):
        """Convert MaxAggregation to JSON format."""
        json_data = {
            "type": "max_aggregation",
            "field": self.field,
            "name": self.name,
            "nested_path": self.nested_path,
            "nested_filter": self.nested_filter
        }

        # ✅ Remove None values
        return {k: v for k, v in json_data.items() if v is not None}

    @classmethod
    def from_json(cls, data):
        """Deserialize JSON data into MaxAggregation object."""
        return cls(
            field=data["field"],
            name=data.get("name"),
            nested_path=data.get("nested_path"),
            nested_filter=data.get("nested_filter")
        )

class CardinalityAggregation(BaseAggregation):
    def __init__(self, field, name=None, precision_threshold=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(field, name, nested_path, nested_filter, aggs)
        self.precision_threshold = precision_threshold

    def to_elasticsearch(self):
        """Convert CardinalityAggregation to an Elasticsearch-compatible format."""
        cardinality_agg = {"cardinality": {"field": self.field}}

        # ✅ Add precision_threshold if present
        if self.precision_threshold is not None:
            cardinality_agg["cardinality"]["precision_threshold"] = self.precision_threshold

        # ✅ Handle nested paths/filters if applicable
        cardinality_agg = self._add_nested_clause(cardinality_agg)

        # ✅ Add sub-aggregations if they exist
        if self.aggs:
            cardinality_agg["aggs"] = build_aggregation_query_class(self.aggs)

        # ✅ Ensure correct wrapping of aggregation under field name
        return {self.name: cardinality_agg} if self.name else {self.field: cardinality_agg}

    def to_json(self):
        """Convert CardinalityAggregation to JSON format."""
        json_data = {
            "type": "cardinality_aggregation",
            "field": self.field,
            "name": self.name,
            "precision_threshold": self.precision_threshold,
            "nested_path": self.nested_path,
            "nested_filter": self.nested_filter
        }

        # ✅ Remove None values
        return {k: v for k, v in json_data.items() if v is not None}

    @classmethod
    def from_json(cls, data):
        """Deserialize JSON data into CardinalityAggregation object."""
        return cls(
            field=data["field"],
            name=data.get("name"),
            precision_threshold=data.get("precision_threshold"),
            nested_path=data.get("nested_path"),
            nested_filter=data.get("nested_filter")
        )

class CompositeAggregation(BaseAggregation):
    def __init__(self, name=None, sources=None, size=10, after=None, order=None, nested_path=None, nested_filter=None, aggs=None):
        super().__init__(None, name, nested_path, nested_filter, aggs)  # No direct field in composite
        self.sources = sources or []
        self.size = size
        self.after = after
        self.order = order  # ✅ Support ordering

    def to_elasticsearch(self):
        """Convert CompositeAggregation to an Elasticsearch-compatible format."""
        composite_agg = {
            "composite": {
                "sources": self.sources,  # ✅ Handle source fields
                "size": self.size
            }
        }

        # ✅ Add optional `after` key for pagination
        if self.after:
            composite_agg["composite"]["after"] = self.after

        # ✅ Add optional ordering dictionary
        if self.order:
            composite_agg["composite"]["order"] = self.order  # Directly store as dictionary

        # ✅ Handle nested paths and filters if applicable
        composite_agg = self._add_nested_clause(composite_agg)

        # ✅ Add sub-aggregations if they exist
        if self.aggs:
            composite_agg["aggs"] = build_aggregation_query_class(self.aggs)

        # ✅ Ensure correct wrapping of aggregation under field name
        return {self.name: composite_agg} if self.name else composite_agg

    def to_json(self):
        """Convert CompositeAggregation to JSON format."""
        json_data = {
            "type": "composite_aggregation",
            "name": self.name,
            "sources": self.sources,
            "size": self.size,
            "after": self.after,
            "order": self.order,
            "nested_path": self.nested_path,
            "nested_filter": self.nested_filter
        }

        # ✅ Remove None values
        return {k: v for k, v in json_data.items() if v is not None}

    @classmethod
    def from_json(cls, data):
        """Deserialize JSON data into CompositeAggregation object."""
        return cls(
            name=data.get("name"),
            sources=data.get("sources"),
            size=data.get("size", 10),  # Default to 10
            after=data.get("after"),
            order=data.get("order"),
            nested_path=data.get("nested_path"),
            nested_filter=data.get("nested_filter")
        )

def create_single_aggregation_object(agg_def, name=None):
    """Creates a single aggregation object from a definition, supporting both traditional and simplified formats."""
    if isinstance(agg_def, dict):
        agg_type = list(agg_def.keys())[0]  # Extract aggregation type
        if agg_type == "terms":
            return TermsAggregation(field=agg_def["terms"]["field"], size=agg_def["terms"].get("size"), name=name)
        elif agg_type == "histogram":
            return HistogramAggregation(
                field=agg_def["histogram"]["field"],
                interval=agg_def["histogram"]["interval"],
                name=name,
                extended_bounds=agg_def["histogram"].get("extended_bounds"),
                min_doc_count=agg_def["histogram"].get("min_doc_count"),
                keyed=agg_def["histogram"].get("keyed")
            )
        # Add other aggregation types here...
        else:
            raise TypeError(f"Unsupported aggregation type '{agg_type}'.")

    elif isinstance(agg_def, list):  # ✅ Handle simplified format
        if len(agg_def) == 2 or len(agg_def) == 5:  # ✅ Extended format
            agg_type, param, *optional_params = agg_def
            if agg_type == "terms":
                return TermsAggregation(field=name, size=param, name=name)
            elif agg_type == "histogram":
                extended_bounds, min_doc_count, keyed = (optional_params + [None, None, None])[:3]  # Ensure optional params
                return HistogramAggregation(
                    field=name, interval=param, name=name,
                    extended_bounds=extended_bounds, min_doc_count=min_doc_count, keyed=keyed
                )
            else:
                raise TypeError(f"Invalid aggregation type '{agg_type}' in simplified format.")
    elif isinstance(agg_def, BaseAggregation):
        return agg_def  # Already an aggregation instance
    else:
        raise TypeError("Invalid aggregation definition. Must be a dictionary, list, or a BaseAggregation instance.")

def create_aggregation_object(agg_data):
    agg_objects = {}

    if isinstance(agg_data, dict):  # Handle a dictionary of aggregations
        for name, agg_def in agg_data.items():
            agg_obj = create_single_aggregation_object(agg_def, name)
            if agg_obj:  # ✅ Ensure the returned object is valid
                agg_objects[name] = agg_obj
            else:
                raise ValueError(f"Invalid aggregation object for '{name}': {agg_def}")  # 🚨 Debugging message

    return agg_objects

def build_aggregation_query_class(aggs_data):
    agg_objects = create_aggregation_object(aggs_data)
    aggs_query = {}
    for name, agg_obj in agg_objects.items():
        aggs_query.update(agg_obj.to_elasticsearch())
    return aggs_query
