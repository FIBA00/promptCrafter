from fastapi import FastAPI, status, Depends, HTTPException
from schema.schemas import PromptSchema, PromptSchemaOutput
from sqlalchemy.orm import Session
from utility.logger import get_logger
from db.database import get_db, engine
from models import models

models.Base.metadata.create_all(bind=engine)

lg = get_logger(__file__)
app = FastAPI()


@app.get("/")
def main():
    return {"message": "Hello from backend!"}


# route for recieving prompts
@app.post("/main/get_started")
def get_prompts(
    db: Session = Depends(get_db), prompt: PromptSchema = None
) -> PromptSchemaOutput:
    # process the prompt here
    if prompt:
        lg.debug(prompt)

    return PromptSchemaOutput(
        structured_prompt="This is a structured prompt based on your input.",
        natural_prompt="This is a natural language prompt based on your input.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
