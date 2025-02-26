from flask import Blueprint
from example_tests_objects import generate_avg_agg_object, generate_bool_filter_object, generate_cardinality_agg_object, generate_composite_agg_object, generate_date_histogram_agg_object, generate_histogram_agg_object, generate_ids_filter_object, generate_match_filter_object, generate_max_agg_object, generate_range_agg_object, generate_range_filter_object, generate_sort_object, generate_sum_agg_object, generate_term_filter_object, generate_terms_agg_object, generate_terms_filter_object, generate_wildcard_filter_object
from transformer import transform, QueryExecutor
import json

home_route = Blueprint('home_route', __name__)

@home_route.route("/", methods=["GET"])
def home():
    transformer = transform.Transformer("my_events")
    query1 = transformer.transform(
        generate_ids_filter_object()
    )
    print(prettify(query1))
    query_executor = QueryExecutor()
    response = query_executor.execute_query(query1)
    return prettify(response.body)  # Return the results

def prettify(query):
    """Prettifies a nested dictionary (like an Elasticsearch query) as JSON."""
    return json.dumps(query, indent=2)  # Use json.dumps with indentation
