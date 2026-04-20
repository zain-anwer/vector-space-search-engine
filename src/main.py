from vector_search import vector_search

result = vector_search('massive inflow of refugees')
for doc_id, sim in result:
    print('DOC_ID: ',doc_id,' similarity: ',sim)