from utils.create_components import create_components
from bigtree import Node, print_tree

def search_query(query):
    query_tree = create_components(query, return_tree=True)
    print_tree(query_tree)