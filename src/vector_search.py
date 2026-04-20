from indexer import generate_index
from data_preprocessing import normalize_data
from pathlib import Path
import json
import math

def vector_search(query):

    # checking for existence of data structures
    # creating them if needed

    if not (Path('index/index.json').exists() and Path('index/idf_dict.json').exists()):
        print('Generating Index')
        generate_index('data/trump_speeches/') 
    else:
        print('Index already generated')
    print('Resuming vector search')

    with open('index/index.json','r') as f:
        index = json.load(f)

    with open('index/idf_dict.json','r') as f:
        idf_dict = json.load(f)

    # normalizing query

    query_tokens = normalize_data(query)

    # generating query vector by tf * idf weights for each term

    query_vector = {}

    for token in query_tokens:
        if token in query_vector:
            query_vector[token] += 1
        else:
            query_vector[token] = 1
        
    doc_list = {}
    query_size = len(query_vector)

    for i, token in enumerate(query_vector.keys()):

        if token in idf_dict and token in index:
            query_vector[token] *= idf_dict[token]
            
            for doc_id in index[token].keys():
                if doc_id not in doc_list:
                    doc_list[doc_id] = [0] * query_size
                
                doc_list[doc_id][i] = index[token][doc_id] * idf_dict[token]
        else:
            query_vector[token] = 0

    # converting dictionary into list for cosine similarity computation
    query_vector_list = list(query_vector.values())

    result_list = []
    
    # calculate query magnitude once outside the loop for efficiency
    query_mag = math.sqrt(sum(w**2 for w in query_vector_list))


    for doc_id, doc_vector in doc_list.items():
        
        # calculate dot product using zip
        dot_product = sum(q * d for q, d in zip(query_vector_list, doc_vector))
        
        # calculate doc magnitude
        doc_mag = math.sqrt(sum(w**2 for w in doc_vector))
        
        # vector search through cosine similarity
        if query_mag > 0 and doc_mag > 0:
            cosine_sim = dot_product / (query_mag * doc_mag)
        else:
            cosine_sim = 0.0

        # filter any docs that don't meet criteria (alpha < 0.005) 
        if cosine_sim >= 0.005:
            result_list.append((doc_id, cosine_sim))

    # Sort so the most relevant documents appear first
    result_list.sort(key=lambda x: x[1], reverse=True)
    
    return result_list