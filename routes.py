from flask import Blueprint
from example_tests_objects import generate_avg_agg_object, generate_bool_filter_object, generate_cardinality_agg_object, generate_composite_agg_object, generate_date_histogram_agg_object, generate_histogram_agg_object, generate_ids_filter_object, generate_match_filter_object, generate_max_agg_object, generate_range_agg_object, generate_range_filter_object, generate_sort_object, generate_sum_agg_object, generate_term_filter_object, generate_terms_agg_object, generate_terms_filter_object, generate_wildcard_filter_object
from transformer import transform
import json

home_route = Blueprint('home_route', __name__)

@home_route.route("/", methods=["GET"])
def home():
    transformer = transform.Transformer("my_index")
    query1 = transformer.transform(
        generate_ids_filter_object()
    )
    query2 = transformer.transform(
        generate_match_filter_object()
    )
    query3 = transformer.transform(
        generate_range_filter_object()
    )
    query4 = transformer.transform(
        generate_term_filter_object()
    )
    query5 = transformer.transform(
        generate_terms_filter_object()
    )
    query6 = transformer.transform(
        generate_wildcard_filter_object()
    )
    query7 = transformer.transform(
        generate_bool_filter_object()
    )
    query8 = transformer.transform(
        generate_sort_object()
    )
    query9 = transformer.transform(
        generate_terms_agg_object()
    )
    query10 = transformer.transform(
        generate_avg_agg_object()
    )
    query11 = transformer.transform(
        generate_range_agg_object()
    )
    query12 = transformer.transform(
        generate_histogram_agg_object()
    )
    query13 = transformer.transform(
        generate_date_histogram_agg_object()
    )
    query14 = transformer.transform(
        generate_sum_agg_object()
    )
    query15 = transformer.transform(
        generate_sum_agg_object()
    )
    query16 = transformer.transform(
        generate_max_agg_object()
    )
    query17 = transformer.transform(
        generate_cardinality_agg_object()
    )
    query18 = transformer.transform(
        generate_composite_agg_object()
    )
    return prettify_query([
        query1, 
        query2, 
        query3, 
        query4, 
        query5, 
        query6, 
        query7, 
        query8, 
        query9, 
        query10, 
        query11, 
        query12, 
        query13,
        query14,
        query15,
        query16,
        query17,
        query18
    ])

def prettify_query(query):
    """Prettifies a nested dictionary (like an Elasticsearch query) as JSON."""
    return json.dumps(query, indent=2)  # Use json.dumps with indentation
