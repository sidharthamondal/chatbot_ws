# Import necessary libraries and modules
import requests  # For making HTTP requests
from . import envVars  # Import environment variables from Chatserver module
from sklearn.feature_extraction.text import TfidfVectorizer  # Import TfidfVectorizer for text vectorization
from sklearn.metrics.pairwise import cosine_similarity  # Import cosine_similarity for comparing text similarity
from sentence_transformers import SentenceTransformer, util



# Define a function to get context based on input data from a Pinecone index
def get_context(input: dict, minScore=0.01):
    # Set the URL for the Pinecone query index API endpoint
    url = envVars.pineconeQueryIndexapiendpoint
    
    try:
        # Send a GET request to the endpoint with the JSON data
        response = requests.get(url, json=input)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            
            # Parse the JSON response
            response = response.json()

            # Extract the context from the response
            filtered_data = []  # Initialize an empty list to store the filtered data
            
            # Iterate through the response data and filter based on the minimum score
            for item in response["data"]:    
                if item["score"] > minScore:
                    filtered_data.append(item)
            
            context = """"""
            # If there is filtered data, concatenate the text from each item
            if len(filtered_data) > 0:
                for item in filtered_data:
                    context = context + item["metadata"]["text"] + " "    
            
            # Return the concatenated context and the filtered data
            return context, filtered_data
        else:
            # Print an error message if the request was not successful
            print(f"Request failed with status code: {response.status_code}")
            return None
    except Exception as e:
        # Print an error message if an exception occurs during the request
        print(f"An error occurred: {str(e)}")
        return None
    

# Define a function to get the most similar chunk from a dictionary based on text similarity
def getMaxSimmilarChunk(text, dictionary):

    # Load a pre-trained sentence transformer model
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # Encode the input text into a vector
    text_vector = model.encode(text, convert_to_tensor=True)

    # Initialize variables to track maximum similarity and the corresponding dictionary item
    max_sim = 0
    max_dict = None

    # Iterate through the items in the input dictionary
    for outer_dict in dictionary:
        d_text = outer_dict['metadata']['text']

        if d_text:
            # Encode the text from the dictionary into a vector
            d_vector = model.encode(d_text, convert_to_tensor=True)

            # Calculate cosine similarity between the input text and the dictionary text
            similarity = util.pytorch_cos_sim(text_vector, d_vector).item()

            # Update maximum similarity and corresponding dictionary item if the current similarity is higher
            if similarity >= max_sim:
                max_sim = similarity
                max_dict = outer_dict

    # Return the metadata of the dictionary item with the maximum similarity
    return max_dict['metadata']