conversationPrompt = """Use the following pieces of context delimited by <context> and </context> to answer the question delimited by <Question>  and </Question> at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
Answer should be small and very precise 
Use the Entity information as well which is the topic for which the question was asked for.
 
Chat history information:
{summary}
This should be in the following format:
Entity information: [entity]
Question: [question here]
Helpful Answer: [answer here]

Begin!
Entity information:{entity}
Context:

---------
<context>{context}</context>
---------
Question: <Question> {question} </Question>  
Helpful Answer:"""

firstBotMessage = """
Hello, Please let me know what are you want to know about ?
"""


secondBotMessage = """
Okay Thanks for confirming.
"""



entityErrorMessage = """
Sorry, we are unable to find anything simmilar to you search. Try again
"""


