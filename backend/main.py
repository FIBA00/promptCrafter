from fastapi import FastAPI
from schema.schemas import PromptSchema, PromptSchemaOutput
from utility.logger import get_logger

lg = get_logger(__file__)

app = FastAPI()


@app.get("/")
def main():
    return {"message": "Hello from backend!"}

# route for recieving prompts 
@app.post('/main/get_started')
def get_prompts(prompt: PromptSchema) -> PromptSchemaOutput:
    # process the prompt here
    if prompt: 
        print(prompt)
    
    return PromptSchemaOutput(
        structured_prompt="This is a structured prompt based on your input.",
        natural_prompt="This is a natural language prompt based on your input."
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)