from bigtree import print_tree
from search.search_query import search_query

if __name__ == "__main__":
    query = """
    A rocket landing system comprising: a rocket,
    and a landing tower comprising a plurality of capture members 
    adapted to catch the rocket on landing, and a landing control system 
    comprising sensors to detect and control the position of the rocket 
    relative to the tower during landing.
    """
    search_query(query)
    #print(results)
