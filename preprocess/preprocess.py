import argparse
import os
import json
from preprocess.database import create_database, clean_database, create_trees_in_database

def main(args):
    if os.path.exists(args.database_in_path):
        print(f"Using database file at path {args.database_in_path}")
        with open(args.database_path, 'r') as file:
            search_results = json.load(file)
    else:
        print("File not found, create new file? no to exit.")
        _in = input('[y/n]')
        if _in == 'y':
            search_results = {}
        else:
            exit()

    database1 = create_database(args.data_path, search_results, args.database_in_path, args.enable_debug)
    database1_cleaned = clean_database(database1, args.only_us, args.enable_debug)
    database2 = create_trees_in_database(database1_cleaned)

    with open(args.database_out_path, 'w') as json_file:
        json.dump(database2, json_file, indent=4)

if __name__ == "__main":
    parser = argparse.ArgumentParser()
    parser.add_argument('--enable_debug',type=bool, help="Bool to determine whether debug logging is enabled (default: false)", default=False)
    parser.add_argument('--data_path', type=str, help="Path to the input file containing patent IDs (default: ../data/data.txt)", default="../data/data.txt")
    parser.add_argument('--database_in_path', type=str, help="Path to the input file for database 1 (default: ../data/database1.json)", default="../data/database1.json")
    parser.add_argument('--only_us',type=bool, help="Bool to only keep US patents in cleaned database (default: false)", default=False)
    parser.add_argument('--database_out_path', type=str, help="Path for the output file for database 2 (default: ../data/database2.json)", default="../data/database2.json")
    args = parser.parse_args()
    main(args)