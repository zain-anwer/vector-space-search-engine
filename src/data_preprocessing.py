# data cleaning and normalization
# proposed method of unicode normalization --> NFKC : compatible decomposition followed by canonical decomposition

import unicodedata           # for removing diacritics and stuff
import re                    # for removing punctuation
import spacy                 # for lemmitization

# loading spaCy model once to improve latency
model = spacy.load('en_core_web_sm',disable=['parser','ner'])

# stop word list
with open('data/stop_words.txt','r') as file:
    stop_words = file.read()
    # splitting on multiple basis just to be sure
    stop_list = re.split(r'[\n\s]+',stop_words)

def normalize_data(data : str):

    # removing diacritics
    data = unicodedata.normalize('NFKC',data)
    
    # converting to lowercase
    data = data.lower()

    # this function substitutes a given pattern for another
    # we subsitute everything with nothing '' except for alphanumeric characters and spaces

    data = re.sub(r'[^a-z0-9\s]','',data)

    # removing multiple spaces and beginning and ending spaces
    data = re.sub(r'\s+',' ',data)
    data = data.strip()

    # tokenization --> lemmitization --> stopword removal
    doc = model(data)

    tokens = [token.lemma_ for token in doc if token.lemma_ not in stop_list]

    return tokens
    

#-------------------------------------- module testing code -----------------------------------------------------#

tokens = normalize_data('I @really@ really really really really really!!! like youu do you want me? "Hell yeah"')
print(tokens)