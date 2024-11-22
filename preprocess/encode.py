import os
import json
import faiss
import numpy as np
from tqdm import tqdm
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain.docstore.document import Document
from dotenv import load_dotenv
load_dotenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
embedding_function = OpenAIEmbeddings(
    model='text-embedding-ada-002',
    api_key=openai_api_key
)

def save_to_faiss(args):
    with open(args.database2, 'r') as f:
        data2 = json.load(f)
    
    metadata = []
    texts = []
    
    for i, element in tqdm(enumerate(data2)):
        if not data2[i].get('all_indp_claim_components'):
            continue
        for j, system_component_list in enumerate(data2[i]['all_indp_claim_components']):
            component_list_conc = ",".join(system_component_list)
            metadata.append({
                "key": element['key'],
                "claim_num": j,
                "encoded_text": component_list_conc
            })
            texts.append(component_list_conc) 

    embeddings = embedding_function.embed_documents(texts)
    embeddings_np = np.array(embeddings).astype('float32')
    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)
    faiss.write_index(index, args.vdatabase)

    with open(args.vdatabase_meta, 'w') as f:
        json.dump(metadata, f)

def save_to_pinecone(args):
    embedding_function = OpenAIEmbeddings(
        model='text-embedding-ada-002',
        api_key=openai_api_key
    )
    pc = Pinecone(api_key=pinecone_api_key)
    pc.delete_index(args.v_index)
    pc.create_index(
        args.v_index, 
        dimension=1536, 
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ) 
    )
    index = pc.Index(args.v_index)

    with open(args.database2, 'r') as f:
        data2 = json.load(f)
    data2_doc = []

    for i, element in tqdm(enumerate(data2)):
        for j, system_component_list in enumerate(data2[i]['all_indp_claim_components']):
            component_list_conc = " ".join(system_component_list)
            doc = Document(
                page_content=component_list_conc,
                metadata={
                    "key": element['key'],
                    "images": data2[i]['images'],
                    "abstract": data2[i]['abstract'],
                    "description_link": data2[i]['description_link'],
                    "indp_claim_num": data2[i]['indp_claims'][j]['claim_number'],
                    "indp_claim_text": data2[i]['indp_claims'][j]['claim_text'],
                    "indp_claim_components": data2[i]['all_indp_claim_components'][j],
                }
            )
            data2_doc.append(doc)

    texts = [doc.page_content for doc in data2_doc]  
    embeddings = embedding_function.embed_documents(texts)
    vectors = []
    for i, doc in enumerate(data2_doc):
        metadata = doc.metadata
        vectors.append((metadata['key'], embeddings[i], metadata))

    batch_size = 100  
    for i in tqdm(range(0, len(vectors), batch_size)):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
