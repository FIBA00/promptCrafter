# Procssing prompt

import uuid
from fastapi import APIRouter, status, Depends, HTTPException
from schema.schemas import PromptSchema, PromptSchemaOutput, UserPrompts
from sqlalchemy.orm import Session
from utility.logger import get_logger
from db.database import get_db
from services.prompt_service import PromptService
from services.restructure_prompt_service import RestructuredPromptService

router = APIRouter(prefix="/process_prompt", tags=["process"])
prompt_service = PromptService()
st_prompt_service = RestructuredPromptService()
lg = get_logger(__file__)


# route for recieving prompts
@router.post("/", status_code=status.HTTP_200_OK, response_model=PromptSchemaOutput)
def create_new_prompt(
    db: Session = Depends(get_db), prompt_data: PromptSchema = None
) -> PromptSchemaOutput:
    # process the prompt here, and create dependency current_user, to keep track of users.
    # user = get_current_user()

    # TODO: step 1 : check if the current session has user id with the request

    # step 2 : if there is no id and user has sent the prompt create user id
    # Note: We rely on the global exception handler in main.py to catch and log any DB errors
    # This keeps our router code clean and the logging consistent.

    new_prompt = prompt_service.save_prompt(session=db, prompt_data=prompt_data)

    # step 3 : update the user, prompt, structured_prompt tables with new information
    st_prompt = st_prompt_service.create_structured_prompt(
        session=db, prompt_data=new_prompt
    )
    return st_prompt

    # Removed localized try-except block to allow full traceback logging in main.py


# NOTE: so instead of separately returning the prompt and structured prompt for this routes
# we can create schema to return all the info related to the prompt id
# since author_id is tied to the restructured prompt and non structured prompt


@router.get("/", status_code=status.HTTP_200_OK, response_model=UserPrompts)
def get_all_prompt(db: Session = Depends(get_db)) -> UserPrompts:
    # get historical prompts
    # TODO: this requeires user id  dependency to retrieve the desired prompt
    # prompt_service.get_all_prompt(session=db)
    pass


# we can use query param to get the recent prompts or any parameter
@router.get("/")
def get_one_prompt(db: Session = Depends(get_db)):
    # get one historical prompts
    # st_prompt_service.get_one_structured_prompt_by_user_id(id=user_id, session=db, prompt_id=prompt_id)
    pass


@router.delete("/{prompt_id}")
def delete_one_prompt():
    pass
