# Import all modules from the 'imports' package
from imports import *
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse


app = FastAPI()
# Dictionary to store active users and their corresponding user IDs
active_users = {}

# Dictionary to store chat language models for each user
chat_llms = {}

# Dictionary to store information about the current chat entity for each user
chat_entity = {}

# Dictionary to store active chat sessions
chat_sessions = {}

# Dictionary to store chat history
chat_history = {}

chat_user_entity = {}

# Schema definition for input validation


def concatenate_values(input_data):
    output_string = ""
    for values_list in input_data.values():
        for value in values_list:
            output_string += value + ' '
    return output_string.strip()


# Function to get or generate a user ID based on the WebSocket connection
def get_user_id(websocket):
    if websocket not in active_users:
        user_id = uuid.uuid4().hex
        active_users[websocket] = user_id
    return active_users[websocket]

# Function to initialize the chatbot for a user
async def init_chatbot(websocket, user_id):
    # TODO: Define the PromptTemplate and OpenAI parameters
    prompt = PromptTemplate(input_variables=["summary","context","question","entity"], template=prompts.conversationPrompt)
    llm = OpenAI(openai_api_key=envVars.openaiKey, temperature=0.2, model_name=envVars.modelUse)
    
    # Initialize a language model chain for the user and store it in chat_llms dictionary
    agent = LLMChain(llm=llm, prompt=prompt, verbose=True, memory=ChatMemoryClass())
    chat_llms[user_id] =  agent  

# Function to initialize the entity extractor for a user

# WebSocket handler function for the chatbot
    
@app.websocket("/ws")
async def chatbot(websocket: WebSocket):
    await websocket.accept()
    user_id = get_user_id(websocket)
   
    # Initialize the chatbot for the user if not already done
    if user_id not in chat_llms:
        await init_chatbot(websocket, user_id)
  
    llm = chat_llms[user_id]
    chat_id = str(uuid.uuid4())
    chat_sessions[chat_id] = websocket
    chat_history[chat_id] = []
    chat_user_entity[user_id]={}
    chat_entity[user_id]= {}
    try:
        # Handle incoming messages from the WebSocket connection
        while True:
            payload = await websocket.receive_json()
            
            message = payload["message"]
            agentid = payload["agentId"]
            organizationid = payload["organizationId"]  
            
            if not chat_user_entity[user_id]:
                chat_user_entity[user_id] = entityExtractor.chatUserEntity(organizationid,agentid)
            # Initialize entity extraction and handle the results
            
            results = entityExtractor.find_matching_field_in_text(message,chat_user_entity[user_id])
            print(results)
            if results:
                if Counter(chat_entity[user_id]) != Counter(results):
                    chat_entity[user_id]=results
                    print(results)
                    await websocket.send_text(prompts.secondBotMessage )
                
            else:
                # If entity extraction fails, check if there is a stored entity for the user
                if user_id not in chat_entity.keys():
                    await websocket.send_text(prompts.entityErrorMessage)
                else:
                    # Use QnA cache to retrieve or generate a response
                    try:
                        dynamic_cache = QnACache()
                        
                        tag = str(agentid) + "_" + str(organizationid) + "_" + concatenate_values(chat_entity[user_id])
                        query = (
                            Query(f"@tag:{{{tag}}} @vector:[VECTOR_RANGE $radius $vec]=>{{ $YIELD_DISTANCE_AS: score }}")
                                        .sort_by("score")
                                        .return_fields("score","answer")
                                        .paging(0, 1)
                                        .dialect(2)
                                    )
                        query_vector = dynamic_cache.vectorize_sentence(message)
                        query_params = {
                            "radius": 0.3,
                            "vec": query_vector.tobytes()
                        }
                
                        search_result = dynamic_cache.search_qna(query, query_params)
                        del dynamic_cache
                    except Exception as e:
                        print(e)
                        search_result = None


                    # If a cached answer is found, send it back to the user
                    if search_result:
                        print("sent from cache")
                        
                        cachedAnswer = json.loads(search_result[0]['answer'])
                        await websocket.send_json(json.dumps(cachedAnswer))
                    else:
                        # If no cached answer, retrieve context and run the language model
                        contextBuild = {
                            "organizationId":organizationid,
                            "agentId":agentid,
                            "query":message,
                            "top_k":3,
                            "metadata":{"doc":chat_entity[user_id]}
                        }
                        context, pineconeResponse = get_context(contextBuild)
                        llmResponse = llm.run({"context": context, "question": message,"entity":chat_entity[user_id]})
                        
                        # Process the responses and send the final response to the user
                        response = getMaxSimmilarChunk(llmResponse, pineconeResponse)
                        response['llmresponse'] = llmResponse
                            
                        # Store the QnA pair in the cache for future use
                        try:
                            dynamic_cache = QnACache()
                            dynamic_cache.store_qna(agentid, organizationid,concatenate_values(chat_entity[user_id]), message, json.dumps(response))
                            del dynamic_cache
                        except:
                            print("server not working")
                        await websocket.send_json(json.dumps(response))
                
    finally:
        # Clean up resources when the chat session ends
        del chat_sessions[chat_id]
        del chat_history[chat_id]


# Comment this code if running inside docker container
if __name__ == "__main__":
    import uvicorn
        

    # Uncomment the line below to run the WebSocket server with Uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")