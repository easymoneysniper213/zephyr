import os
from dotenv import load_dotenv
import argparse
import json
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm
from dotenv import load_dotenv
import faiss
import numpy as np
from utils.create_components import create_components
from utils.compare_components import compare_components

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
embedding_function = OpenAIEmbeddings(
    model='text-embedding-ada-002',
    api_key=openai_api_key
)

def search_faiss(query, faiss_index_path, metadata_path, top_k):
    with open(metadata_path, 'r') as f:
        metadatas = json.load(f)

    query_embedding = np.array(embedding_function.embed_query(query)).reshape(1, -1)
    faiss_index = faiss.read_index(faiss_index_path)
    distances, indices = faiss_index.search(query_embedding, top_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        results.append({
            'id': metadatas[idx], 
            'score': dist          
        })

    results = sorted(results, key=lambda x: x['score'], reverse=False)
    return results

def main(args):
    query = """
    A device for converting wave energy to compressed air comprising:
    a compression chamber comprising an upper end and a lower end at opposing ends of an axis, wherein the upper end comprises a one-way air inlet valve and a one-way compressed air outlet valve, and wherein the lower end comprises a one-way air inlet valve and a one-way compressed air outlet valve;
    a piston that divides the compression chamber into upper and lower variable-pressure sub-chambers, wherein the piston is operable within the compression chamber between the upper end and the lower end;
    a float external to the compression chamber;
    a shaft connected between the piston and the float;
    a compressed air storage tank connected to the one-way compressed air outlet valves; and
    an intelligent control comprising:
    a tidal sensor for capturing and/or monitoring tidal data associated with the ocean water;
    a data analytics module for storing, transmitting, and communicating said tidal data, and
    a calibration module for calibrating and/or re-calibrating the device so as to achieve a weightlessness effect at a crest position of a wave;
    wherein ocean water acting upon the float is used to create a weight for capturing force of gravity in the lower variable-pressure sub-chamber and said ocean water is mixed with ambient air in the float so as to achieve the weightlessness effect at the crest position of the wave;
    wherein the ambient air is used in the lower variable-pressure sub-chamber to utilize buoyancy so as to lift the float.
    """
    query = query.replace("\n", " ")
    query_components = create_components(query)
    print(query_components)
    print("-------------------")
    query_components_str = " ".join(query_components)
    ranked_list = search_faiss(query_components_str, args.database, args.metadata, args.topk)

    '''
    with open('output.txt', 'w') as file:
        for item in ranked_list:
            file.write(f"{item}\n")
    '''
    for item in ranked_list:
        comparison_table = compare_components(args.database2, query_components, item, args.t_threshold)
        print(item)
        print("-------------------")
        print(comparison_table)
        break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--database',type=str, help="path for testing data (default: test_data.json)", default="./data/vdatabase.index")
    parser.add_argument('--metadata',type=str, help="path for testing data (default: test_data.json)", default="./data/vdatabase_meta.json")
    parser.add_argument('--database2',type=str, help="path for testing data (default: database2_dict.json)", default="./data/database2_dict.json")
    parser.add_argument('--topk',type=int, help="path for testing data (default: test_data.json)", default=20)
    parser.add_argument('--t_threshold',type=int, help="path for testing data (default: test_data.json)", default=0.2)
    args = parser.parse_args()
    main(args)

