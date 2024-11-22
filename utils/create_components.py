import os
from dotenv import load_dotenv
from openai import OpenAI
import re
from dotenv import load_dotenv
from bigtree import Node, tree_to_dict, list_to_tree
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def clean_up_tree(node):
    for child in list(node.children):
        clean_up_tree(child)
        child.parent = None
    node.children = []

def not_correct_format(response):
    lines = response.strip().split("\n")
    pattern = r"^\s*-\s*.*$"
    for line in lines:
        if not re.match(pattern, line):
            return True
    return False

def construct_path_list(hierarchy):
    lines = hierarchy.strip().split("\n")
    stack = [""]
    path_list = []

    for line in lines:
        depth = line.count("    ") 
        label = line.strip("- ").strip()
        
        while len(stack) <= depth:
            stack.append(None)

        parent_path = stack[depth - 1] if depth > 0 else ""
        current_path = f"{parent_path}/{label}".strip("/") 
        stack[depth] = current_path
        path_list.append(current_path)
    
    root_nodes = {path.split('/')[0] for path in path_list}
    if len(root_nodes) > 1: 
        path_list = [f"root/{path}" for path in path_list]

    return path_list

def create_tree_from_components(root, hierarchy):
    #clean_up_tree(root) 
    path_list = construct_path_list(hierarchy)
    root = list_to_tree(path_list)
    return root

def get_gpt_response(query):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": 
                    """
                    You will receive an independent claim from a patent. 
                    Based on this claim, create a component composition list, 
                    making sure to break the composition down into unique components,
                    components can have sub components, ensure all text is lowercase.
                    it should be in the following structure:
                    - ...
                        - ...
                        - ...
                    - ...
                        - ...
                    - ...
                    No other text other than this list is needed.
                    all component paths should be unique, combine paths if needed
                    """
            },
            {
                "role": "user", 
                "content": query
            }
        ]
    )
    return response.choices[0].message.content

def create_components(query, return_tree=False):
    root = Node("root")
    content_message = get_gpt_response(query)
    '''
    query_system_components = [
        re.sub(r'^[-\d)\.]+\s*', '', item.strip()) 
        for item in content_message.split("\n") if item.strip()
    ]
    return query_system_components
    '''
    max_retries = 0
    while(not_correct_format(content_message) and max_retries < 3):
        content_message = get_gpt_response(query)
        max_retries += 1

    tree = create_tree_from_components(root, content_message)
    if return_tree:
        return tree
    tree_dict = tree_to_dict(tree)
    return tree_dict