class Sort:
    def __init__(self, field, order="asc", mode=None, format=None, numeric_type=None,
                 nested_path=None, nested_filter=None, missing=None, unmapped_type=None,
                 script=None, lang="painless", params=None, type=None):
        self.field = field
        self.order = order
        self.mode = mode
        self.format = format
        self.numeric_type = numeric_type
        self.nested_path = nested_path  # ✅ Will be handled correctly now
        self.nested_filter = nested_filter  # ✅ Will be wrapped properly
        self.missing = missing
        self.unmapped_type = unmapped_type
        self.script = script
        self.lang = lang if lang else "painless"  # ✅ Ensure lang is not `null`
        self.params = params
        self.type = type

    def to_elasticsearch(self):
        """Converts the Sort object to an Elasticsearch-compatible dictionary."""
        
        # ✅ FIX: Handle `_script` sorting properly
        if self.script:
            script_obj = {
                "_script": {
                    "script": {
                        "source": self.script,
                        "lang": self.lang
                    },
                    "order": self.order
                }
            }
            if self.params:
                script_obj["_script"]["script"]["params"] = self.params
            if self.type:
                script_obj["_script"]["type"] = self.type  # ✅ Ensure "type" is set properly
            
            return script_obj

        # ✅ Regular field-based sorting
        sort_query = {self.field: {"order": self.order}}

        if self.mode:
            sort_query[self.field]["mode"] = self.mode
        if self.format:
            sort_query[self.field]["format"] = self.format
        if self.numeric_type:
            sort_query[self.field]["numeric_type"] = self.numeric_type
        if self.missing:
            sort_query[self.field]["missing"] = self.missing
        if self.unmapped_type:
            sort_query[self.field]["unmapped_type"] = self.unmapped_type

        # ✅ FIX: Ensure `nested_path` is placed inside a `nested` object
        if self.nested_path or self.nested_filter:
            sort_query[self.field]["nested"] = {"path": self.nested_path}
            if self.nested_filter:
                sort_query[self.field]["nested"]["filter"] = self.nested_filter

        return sort_query

    def to_json(self):
        json_data = {
            "type": "sort",
            "field": self.field,
            "order": self.order
        }
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
            if self.params:
                json_data["params"] = self.params
            if self.type:
                json_data["type"] = self.type
        return json_data

    @classmethod
    def from_json(cls, data):
        return cls(
            field=data["field"],
            order=data.get("order", "asc"),
            mode=data.get("mode"),
            format=data.get("format"),
            numeric_type=data.get("numeric_type"),
            nested_path=data.get("nested_path"),
            nested_filter=data.get("nested_filter"),
            missing=data.get("missing"),
            unmapped_type=data.get("unmapped_type"),
            script=data.get("script"),
            lang=data.get("lang", "painless"),
            params=data.get("params"),
            type=data.get("type")
        )

def create_sort_object(data):
    return Sort(
        field=data["field"],
        order=data.get("order", "asc"),
        mode=data.get("mode"),
        format=data.get("format"),
        numeric_type=data.get("numeric_type"),
        nested_path=data.get("nested_path"),
        nested_filter=data.get("nested_filter"),
        missing=data.get("missing"),
        unmapped_type=data.get("unmapped_type"),
        script=data.get("script"),
        lang=data.get("lang"),
        params=data.get("params"),
        type=data.get("type")
    )
