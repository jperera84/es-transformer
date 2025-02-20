from flask import Blueprint
from example_tests_objects import generate_bool_filter_object, generate_ids_filter_object, generate_match_filter_object, generate_range_filter_object, generate_term_filter_object, generate_terms_filter_object, generate_wildcard_filter_object
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
    return prettify_query([query1, query2, query3, query4, query5, query6, query7])

def prettify_query(query):
    """Prettifies a nested dictionary (like an Elasticsearch query) as JSON."""
    return json.dumps(query, indent=2)  # Use json.dumps with indentation
