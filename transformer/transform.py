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

        if aggs:
            self.transformation["steps"].append({"aggs": aggs})

        return self.build_elasticsearch_query(filters_list, sort_list, aggs, size)


    def build_elasticsearch_query(self, filters_data, sort_data=None, aggs_data=None, size=20):
        """Builds an Elasticsearch query with optional sorting and ensures a valid query."""

        query = {"query": {}}

        # Ensure at least one filter exists
        if filters_data:
            filter_query = filter.build_filter_query_class(filters_data)
            if filter_query:
                query["query"] = filter_query
        elif not aggs_data:  # Only insert match_all when there are NO aggregations
            query["query"] = {"match_all": {}}

        if sort_data:
            query["sort"] = [sort.to_elasticsearch() for sort in sort_data]

        if aggs_data:
            aggs_query = aggregation.build_aggregation_query_class(aggs_data)
            if aggs_query:
                query["aggs"] = aggs_query

        if size is not None:
            query["size"] = size

        return query

