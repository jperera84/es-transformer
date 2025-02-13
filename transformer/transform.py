from transformer import filter
from transformer import sort
from transformer import aggregation

"""
Example of the data sent for tranformation:
{
    "source": "my_index",
    "filters": {"field1": {"gt": 10}}
}
"""

class Transformer:
    
    def __init__(self, index):
        self.index = index
        self.transformation = {
            "source": index,
            "steps": []
        }
    
    def transform(self, data):
        """Transforms the data based on the provided transformation steps."""
        return self.process_data(data.get("filters", []), data.get("sorts", []), data.get("aggs", {}), data.get("size", 20))

    def process_data(self, filters, sorts, aggs, size):
        """Adds a filter to the transformation steps."""
        filters_list = []
        for filter_data in filters:
            filters_list.append(filter.create_filter_object(filter_data))
        if len(filters_list) > 0:
            self.transformation["steps"].append({"filters": filters_list})
        sort_list = []
        for sort_data in sorts:
            sort_list.append(sort.create_sort_object(sort_data))
        if len(sort_list) > 0:
            self.transformation["steps"].append({"sort": sort_list})
        if aggs:
            self.transformation["steps"].append({"aggs": aggs})
        return self.build_elasticsearch_query(filters_list, sort_list, aggs, size)
        
    def build_elasticsearch_query(self, filters_data, sort_data=None, aggs_data=None, size=20): # changed function signature
        """Builds an Elasticsearch query with optional sorting."""
        query = {"query": {}}
        ids_filter = {}
        filters_data_clear = []
        for filter_data in filters_data:
            if isinstance(filter_data, list):
                if isinstance(filter_data[0], filter.IdsFilter):
                    ids_filter = filter_data[0]
                else:
                    filters_data_clear.append(filter_data)

        filter_query = filter.build_filter_query_class(filters_data_clear)
        if filter_query:
            query["query"] = filter_query

        if sort_data:
            query["sort"] = [sort.to_elasticsearch() for sort in sort_data]

        if ids_filter:
            query["query"].update(ids_filter.to_elasticsearch())

        if aggs_data:
            aggs_query = aggregation.build_aggregation_query_class(aggs_data)
            if aggs_query:
                query["aggs"] = aggs_query

        if size is not None:  # Add size parameter to the query
            query["size"] = size

        return query
