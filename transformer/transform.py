from transformer import filter
from transformer import sort
from transformer import aggregation

class Transformer:
    
    def __init__(self, index):
        self.index = index
    
    def transform(self, data):
        """Transforms the data based on the provided transformation steps."""
        return self.process_data(data.get("filters", []), data.get("sorts", []), data.get("aggs", {}), data.get("size", 20))

    def process_data(self, filters, sorts, aggs, size):
        """Adds a filter to the transformation steps and ensures a valid query."""

        filters_list = []

        # ✅ Handle both dictionary (OR) and list (AND)
        if isinstance(filters, dict):  # OR condition (should)
            created_filter = filter.create_filter_object(filters)
            if created_filter:
                filters_list.append(created_filter)

        elif isinstance(filters, list):  # AND condition (must)
            for filter_data in filters:
                created_filter = filter.create_filter_object(filter_data)
                if created_filter:
                    filters_list.append(created_filter)

        sort_list = []
        for sort_data in sorts:
            sort_list.append(sort.create_sort_object(sort_data))

        return self.build_elasticsearch_query(filters_list, sort_list, aggs, size)

    def build_elasticsearch_query(self, filters_list, sort_list, aggs, size):
        query_body = {}

        # ✅ Apply filters if they exist
        if filters_list:
            query_body["query"] = filter.BoolFilter(must=filters_list).to_elasticsearch()
        elif aggs:  
            query_body["size"] = 0  # ✅ Force size=0 if only aggregations exist
        else:
            query_body["query"] = {"match_all": {}}  # ✅ Ensure valid query

        # ✅ Apply sorting if present
        if sort_list:
            query_body["sort"] = [sort_obj.to_elasticsearch() for sort_obj in sort_list]

        # ✅ Apply aggregations if present
        if aggs:
            query_body["aggs"] = aggregation.build_aggregation_query_class(aggs)

        return query_body
