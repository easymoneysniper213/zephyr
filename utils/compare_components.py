import json
import os
from dotenv import load_dotenv
import faiss
from langchain_openai import OpenAIEmbeddings
import numpy as np
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
embedding_function = OpenAIEmbeddings(
    model='text-embedding-ada-002',
    api_key=openai_api_key
)

def compare_components(database2_path, query_components, patent_info, term_threshold):
    with open(database2_path, 'r') as f:
        data = json.load(f) 

    patent_id = patent_info['id']['key']
    claim_id = patent_info['id']['claim_num']
    patent_components = data[patent_id]['all_indp_claim_components'][claim_id]
    K = len(patent_components)

    all_results = {}
    patent_embeddings = embedding_function.embed_documents(patent_components)
    patent_embeddings_np = np.array(patent_embeddings).astype('float32')
    dimension = patent_embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(patent_embeddings_np)

    for component in query_components:
        comparison_results = []
        query_embedding = embedding_function.embed_query(component)
        query_embedding_np = np.array(query_embedding).astype('float32').reshape(1, -1)

        distances, indices = index.search(query_embedding_np, K)
        for i, idx in enumerate(indices[0]):
            term = patent_components[idx]
            score = distances[0][i]
            if score >= term_threshold:
                continue
            comparison_results.append({
                'term': term,
                'score': score
            })
        comparison_results = sorted(comparison_results, key=lambda x: x['score'], reverse=False)
        
        seen_terms = set()
        filtered_results = []
        for result in comparison_results:
            term = result['term']
            if term not in seen_terms:
                seen_terms.add(term)
                filtered_results.append(result)
            else:
                for idx, existing_result in enumerate(filtered_results):
                    if existing_result['term'] == term:
                        if existing_result['score'] > result['score']:
                            filtered_results[idx] = result
                        break

        if filtered_results:
            all_results[component] = filtered_results
        else:
            all_results[component] = []

    pairs = []
    for key, value in all_results.items():
        if value:
            pairs.append((key, value[0]['term']))
        else:
            pairs.append((key, None))

    matched_terms = {pair[1] for pair in pairs if pair[1] is not None}
    unmatched_terms = [term for term in patent_components if term not in matched_terms]
    if unmatched_terms:
        pairs.append(('others', unmatched_terms))

    return pairs
        