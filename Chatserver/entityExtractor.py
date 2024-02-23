import json
from fuzzywuzzy import fuzz
import json
import requests
from . import envVars
# import envVars
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer, util
from fuzzywuzzy import fuzz

def preprocess_json_data(json_data):
    # Initialize a dictionary to store keys and values separately
    key_values_dict = {}

    # Iterate through the data
    for key, value in json_data["data"].items():
        for field, val in value.items():
            # If the field is not present in the dictionary, initialize it as an empty list
            key_values_dict.setdefault(field, [])

            # Append the value to the list for the corresponding field
            key_values_dict[field].append(val)

    return key_values_dict

def find_matching_field_in_text(text, json_data, threshold=0.5):
    # Preprocess the JSON data to get a dictionary of keys and values
    key_values_dict = preprocess_json_data(json_data)

    # Use a pre-trained sentence transformer model
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # Encode the input text
    input_embedding = model.encode(text, convert_to_tensor=True)

    # Initialize a dictionary to store the maximum matching value for each key
    max_matching_field = {"key": None, "values": [], "similarity": 0}

    # Iterate through the keys and values dictionary
    for key, values in key_values_dict.items():
        for val in values:
            # Encode the value
            value_embedding = model.encode(val, convert_to_tensor=True)

            # Calculate cosine similarity between input text and the value
            similarity = util.pytorch_cos_sim(input_embedding, value_embedding).item()

            # Update the maximum similarity and matching values
            if similarity > max_matching_field["similarity"]:
                max_matching_field["similarity"] = similarity
                max_matching_field["key"] = key
                max_matching_field["values"] = [val]
            elif similarity == max_matching_field["similarity"]:
                max_matching_field["values"].append(val)

    # If the maximum similarity is above the threshold, return the result
    if max_matching_field["similarity"] >= threshold:
        return {max_matching_field["key"]: max_matching_field["values"]}
    else:
        return None

def chatUserEntity(orgId,agentID):
    url = envVars.getagentkbmetadataurl
    input = {        
    "organizationId":orgId,
    "agentId":agentID
    }
    response = requests.get(url, json=input)
    response = response.json()
    return response



# orgId = "3d8a4601c74e50eb9b459070ef6de5d8"
# agentId ="a019a75d264d50398398e9c0c3ee514d"
# url = "http://34.130.80.81:5000/getagentkbmetadata"

# text_input = "Hi I am looking for and ss and atest and adadss"
# print(chatUserEntity(orgId,agentId))

