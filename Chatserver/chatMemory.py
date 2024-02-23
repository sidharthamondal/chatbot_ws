from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMemory
from pydantic import BaseModel
# from noconflict import classmaker
from typing import List, Dict, Any
import requests
from langchain.llms import OpenAI
import nltk
nltk.download('punkt')
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.utils import get_stop_words

# class ChatMemoryClass(BaseMemory, BaseModel):
#     """Memory class for storing information about entities."""

#     # Define dictionary to store information about entities.
#     summary: dict = {}
#     # Define key to pass information about entities into prompt.
#     memory_key: str = "summary"

#     def clear(self):
#         self.summary = {}

#     @property
#     def memory_variables(self) -> List[str]:
#         """Define the variables we are providing to the prompt."""
#         return [self.memory_key]

#     def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
#         """Load the memory variables, in this case the entity key."""
#         # Get the input text and run through spaCy
#         ### THIS FUNCTION RETURNS WHEN ITS SENDS THE CONTEXT TO LLM
        
#         # Extract known information about entities, if they exist.
#         # entities = [
#         #     self.entities[str(ent)] for ent in doc.ents if str(ent) in self.entities
#         # ]
#         # Return combined information about entities to put into context.
        
#         if 'text' in self.summary.keys():
#             text = self.summary['text']
#         else:
#             text =  ""
#         return {self.memory_key:text}

#     def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
#         """Save context from this conversation to buffer."""
#         #### THIS RUNS WHEN IT SAVES THE CONTEXT
#         text_input = inputs['question']
#         text_output = outputs['text']

#         url = "http://localhost:8000/generate"  # Update with your server's URL if needed

#         conv = text_input + " " + text_output
#         data = {"text": """System: Help the user to summarise and reduce the text provided dont make up answers use this text info only 
#             text:  """ + conv + """ 
#             <summary>:""", "max_tokens": 500}
#         response = requests.post(url, json=data)
#         if response.status_code == 200:
#             result = response.json()
#             summaryText = result["response"]['choices'][0]['text']
#             summaryText = summaryText[summaryText.find("<summary>")+len("<summary>: "):summaryText.find("</summary>")]
#         else: 
#             summaryText = conv

#         if 'text' in self.summary.keys():
            
#             previous_text = self.summary['text'] 
            
#             self.summary['text'] = previous_text + " " + summaryText
    
#         else:
#             self.summary['text'] = summaryText


class ChatMemoryClass(BaseMemory, BaseModel):
    """Memory class for storing information about entities."""

    # Define dictionary to store information about entities.
    summary: dict = {}
    # Define key to pass information about entities into prompt.
    memory_key: str = "summary"

    def clear(self):
        self.summary = {}

    @property
    def memory_variables(self) -> List[str]:
        """Define the variables we are providing to the prompt."""
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """Load the memory variables, in this case the entity key."""
        # Get the input text and run through spaCy
        ### THIS FUNCTION RETURNS WHEN ITS SENDS THE CONTEXT TO LLM
        
        
        if 'text' in self.summary.keys():
            text = self.summary['text']
        else:
            text =  ""
        return {self.memory_key:text}

    # Function to summarize a given text
    def summarize_text(self,text, num_sentences=5):
        # Initialize the parser and tokenizer
        parser = PlaintextParser.from_string(text, Tokenizer("english"))

        # Initialize the LexRankSummarizer with English stop words
        summarizer = LexRankSummarizer()
        summarizer.stop_words = get_stop_words("english")

        # Generate the summary
        summary = summarizer(parser.document, num_sentences)

        # Convert the summary to a string
        summarized_text = ""
        for sentence in summary:
            summarized_text += str(sentence) + " "

        return summarized_text




    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        #### THIS RUNS WHEN IT SAVES THE CONTEXT
        text_input = inputs['question']
        text_output = outputs['text']

        

        if 'text' in self.summary.keys():
            
            previous_text = self.summary['text'] 

            text = text_input + " " + text_output + " " + previous_text
            summaryText = self.summarize_text(text)
            self.summary['text'] = summaryText
    
        else:
            text = text_input + " " + text_output
            summaryText = self.summarize_text(text)
            self.summary['text'] = summaryText
            self.summary['text'] = summaryText