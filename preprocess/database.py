import os
import json
import re
from tqdm import tqdm
from serpapi import GoogleSearch
from utils.create_components import create_components
from utils.handle_errors import save_errors
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('SERPAPI')
openai_api_key = os.getenv("OPENAI_API_KEY")


def create_database(data_path, database, database_path, enable_debug, use_epoch=False, save_epoch=100):
    error_count = 0
    error_list = []

    with open(data_path, 'r') as file:
        count = 0
        for line in tqdm(file):
            line = line.strip()
            patent_id = f"US{line}"
            patent_search_val = f"patent/{patent_id}/en"

            if [patent_id] in database:
                print(f"{patent_id} already exists, skipping...")
                count -= 1
                continue

            params = {
                "api_key": api_key,
                "engine": "google_patents_details",
                "patent_id": patent_search_val
            }
            search = GoogleSearch(params)
            results = search.get_dict()
                
            if results.get('error'):
                error += 1
                error_list.append(patent_id)
            else:
                database[patent_id] = results

            count += 1
            if count % save_epoch == 0 and use_epoch:
                with open(database_path, 'w') as json_file:
                    json.dump(database, json_file, indent=4)
                print(f"Saved {count} results to {database_path}.")
            # if use_epoch==True: remember to add another outside of final loop to ensure final batch is saved

    print(f"Completed search results for {data_path} | Final size: {len(database)}.")
    save_errors(enable_debug, error_count, error_list, 1)
    return database


def get_indp_claim(claim_list):
    if claim_list == None:
        return
    dep_claim_pattern = re.compile(r"claim \d+")
    claim_text_pattern = r"(\d+)[.:]\s*(.*)"
    indp_claims = []
    for claim in claim_list:
        if not dep_claim_pattern.search(claim):
            claim = claim.replace("\n", " ")
            match = re.match(claim_text_pattern, claim)
            if match:
                number = int(match.group(1)) 
                text = match.group(2)
                if "(canceled)" in text:                        # could be improved
                    continue
                indp_claims.append({
                    "claim_number": number,
                    "claim_text": text
                })
    return indp_claims


def clean_database(database, only_us, enable_debug):
    cleaned_data = []
    error_list = []
    error_count = 0

    for key, value in database.items():
        if only_us and not re.search(r"US", key):
            error_list.append({key})
            error_count += 1
            continue
        extracted_item = {
            "key": key,
            "claims": value.get("claims", None),
            "images": value.get("images", None),
            "abstract": value.get("abstract", None),  
            "description_link": value.get("description_link", None),
            "indp_claims": get_indp_claim(value.get("claims"))
        }
        cleaned_data.append(extracted_item)

    save_errors(enable_debug, error_count, error_list, 2)
    print(f"Cleaned database")
    return cleaned_data


def create_trees_in_database(database):
    for record in tqdm(database):
        indp_claims = record['indp_claims']
        all_indp_claim_trees = []
        if indp_claims == None:
            continue
        for claim in indp_claims:
            claim_text = claim.get('claim_text', '')
            if claim_text == None or '':
                continue
            else:
                tree_dict = create_components(claim_text)
                all_indp_claim_trees.append(tree_dict)
            #break
        record['all_indp_claim_trees'] = all_indp_claim_trees
    print(f"Processing complete")
    return database


