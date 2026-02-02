from fastapi import APIRouter, status, Depends, HTTPException
from schema.schemas import PromptSchema, PromptSchemaOutput
from sqlalchemy.orm import Session
from utility.logger import get_logger
from db.database import get_db

router = APIRouter(prefix="/process_prompt", tags=["process"])
lg = get_logger(__file__)


# route for recieving prompts
@router.post("/", status_code=status.HTTP_200_OK, response_model=PromptSchemaOutput)
def get_prompts(
    db: Session = Depends(get_db), prompt: PromptSchema = None
) -> PromptSchemaOutput:
    # process the prompt here
    if prompt:
        lg.debug(prompt)

    prompt = PromptSchema(**prompt.dict())
    db.add(prompt)
    db.commit()
    db.refresh(prompt)

    return PromptSchemaOutput(
        structured_prompt="This is a structured prompt based on your input.",
        natural_prompt="This is a natural language prompt based on your input.",
    )
