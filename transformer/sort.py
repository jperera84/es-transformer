class Sort:  # New class for sort definitions
    def __init__(self, field, order="asc", mode=None, format=None, numeric_type=None, nested_path=None, nested_filter=None, missing=None, unmapped_type=None, script=None, lang="painless", params=None, type=None):
        self.field = field
        self.order = order
        self.mode = mode
        self.format = format
        self.numeric_type = numeric_type
        self.nested_path = nested_path
        self.nested_filter = nested_filter
        self.missing = missing
        self.unmapped_type = unmapped_type
        self.script = script
        self.lang = lang
        self.params = params
        self.type = type

    def to_elasticsearch(self):
        if self.field == "_score":  # Special case for _score
            return {"_score": {"order": self.order}}
        elif self.script:  # handle script sort (Corrected)
            script_clause = {"source": self.script}  # Correct _script structure
            if self.lang:
                script_clause["lang"] = self.lang
            if self.params:
                script_clause["params"] = self.params
            return {"_script": {"script": script_clause, "type": self.type, "order": self.order}}  # Correct _script structure with type and order outside
        else:
            sort_clause = {self.field: {"order": self.order}}
            if self.mode:
                sort_clause[self.field]["mode"] = self.mode
            if self.format:
                sort_clause[self.field]["format"] = self.format
            if self.numeric_type:
                sort_clause[self.field]["numeric_type"] = self.numeric_type
            if self.nested_path:
                sort_clause["nested_path"] = self.nested_path
            if self.nested_filter:
                sort_clause["nested_filter"] = self.nested_filter
            if self.missing:
                sort_clause[self.field]["missing"] = self.missing
            if self.unmapped_type:
                sort_clause[self.field]["unmapped_type"] = self.unmapped_type
            return sort_clause if isinstance(self.field, str) else self.field  # Handle sorting by object

    def to_json(self):
        json_data = {"type": "sort", "field": self.field, "order": self.order}
        if self.mode:
            json_data["mode"] = self.mode
        if self.format:
            json_data["format"] = self.format
        if self.numeric_type:
            json_data["numeric_type"] = self.numeric_type
        if self.nested_path:
            json_data["nested_path"] = self.nested_path
        if self.nested_filter:
            json_data["nested_filter"] = self.nested_filter
        if self.missing:
            json_data["missing"] = self.missing
        if self.unmapped_type:
            json_data["unmapped_type"] = self.unmapped_type
        if self.script:
            json_data["script"] = self.script
            json_data["lang"] = self.lang
            json_data["params"] = self.params
            json_data["type"] = self.type  # Type outside the script object
        return json_data

    @classmethod
    def from_json(cls, data):
        return cls(data["field"], data["order"], data.get("mode"), data.get("format"), data.get("numeric_type"), data.get("nested_path"), data.get("nested_filter"), data.get("missing"), data.get("unmapped_type"), data.get("script"), data.get("lang"), data.get("params"), data.get("type"))

def create_sort_object(data):
    return Sort(
        data["field"], 
        data.get("order", "asc"), 
        data.get('mode'), 
        data.get('format'), 
        data.get('numeric_type'),
        data.get('nested_path'),
        data.get('nested_filter'),
        data.get('missing'),
        data.get('unmapped_type'),
        data.get('script'),
        data.get('lang'),
        data.get('params'),
        data.get('type')
    )  # default order is "asc" 