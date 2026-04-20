# data extraction and index generation
# index would be a hash map (dictionary) and store doc_id and term frequency pairs
# the idf list for each term would be precomputed and stored beside the dictionary

import re
import json
from math import log
from pathlib import Path
from data_preprocessing import normalize_data

def generate_index(folder_path : str):
    
    N = 56          # number of documents
    idf_dict = {}   # dictionary for storing precomputed idf values
    index = {}      # index for storing (doc_id,term_frequency) key value pairs
    folder : str = Path(folder_path)

    if not folder.is_dir():
        print("Error in opening folder...")

    for file in folder.iterdir():
    
        if file.is_file():
            
            N += 1

            doc_id : int = int(re.search(r'speech_(\d+)',file.name).group(1))
            with open(file,'r') as f:
                content = f.read()
        
            tokens = normalize_data(content)
        
            for token in tokens:
                if token not in index:
                    index[token] = {}
                if doc_id in index[token]:
                    index[token][doc_id] += 1
                else:
                    index[token][doc_id] = 1
    
    for key in index.keys():
        idf_dict[key] = log(len(index[key]),10)/N
        
    # check for the existence of the index folder
    # create if does not exist
    
    output_folder = Path('index')
    output_folder.mkdir(parents=True,exist_ok=True)

    # writing both files

    with open('index/index.json','w') as f:
        json.dump(index,f)  
    
    with open('index/idf_dict.json','w') as f:
        json.dump(idf_dict,f)

# ------------------------------------- module testing code -----------------------------------------------------#

def main():
    generate_index('data/trump_speeches/')

if __name__ == '__main__':
    main()