from flask import Blueprint
from example_tests_objects import generate_bool_filter_object, generate_ids_filter_object, generate_match_filter_object, generate_range_filter_object, generate_term_filter_object, generate_terms_filter_object, generate_wildcard_filter_object
from transformer import transform
import json

home_route = Blueprint('home_route', __name__)

@home_route.route("/", methods=["GET"])
def home():
    transformer = transform.Transformer("my_index")
    query = transformer.transform(
        # generate_ids_filter_object()
        # generate_match_filter_object()
        # generate_range_filter_object()
        # generate_term_filter_object()
        # generate_terms_filter_object()
        generate_wildcard_filter_object()
        # generate_bool_filter_object()
    )
    return prettify_query(query)

def prettify_query(query):
    """Prettifies a nested dictionary (like an Elasticsearch query) as JSON."""
    return json.dumps(query, indent=2)  # Use json.dumps with indentation
