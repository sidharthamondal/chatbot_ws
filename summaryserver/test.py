import asyncio
import llama_cpp
from llama_cpp import Llama
from fastapi import FastAPI

app = FastAPI()

llama_cpp.llama_sample_top_k = 40
llama_cpp.llama_sample_temperature = 0.2
llama_cpp.llama_sample_top_p = 0.4
llama_cpp.llama_sample_repetition_penalty = 1.18
llama_cpp.llama_sample_frequency_and_presence_penalties = 64
model = Llama(
    "summaryserver/orca-mini-3b.ggmlv3.q4_0.gguf.bin",
    n_threads=8,
    temperature=0.2,
    n_batch=128,
)

async def generate_response(text: str, max_tokens: int = 5000):
    output = await asyncio.to_thread(lambda: model(text, max_tokens=max_tokens, stop=["\n", "Question", "Q:"], echo=True))
    return {"response": output}

@app.post('/generate')
async def generate(text_data: dict):
    text = text_data.get("text", "")
    max_tokens = text_data.get("max_tokens", 5000)
    
    response = await generate_response(text, max_tokens)
    return response

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
