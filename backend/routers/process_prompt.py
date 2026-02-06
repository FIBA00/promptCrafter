# Procssing prompt
from typing import List
from fastapi import APIRouter, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from schema.schemas import PromptSchema, PromptSchemaOutput, UserPrompts
from sqlalchemy.orm import Session
from utility.logger import get_logger
from db.database import get_db
from services.prompt_service import PromptService
from services.restructure_prompt_service import RestructuredPromptService

router = APIRouter(prefix="/pcrafter", tags=["process"])
# router.mount("/static", StaticFiles(directory="static"), name="static")
prompt_service = PromptService()
st_prompt_service = RestructuredPromptService()
lg = get_logger(__file__)

# Note: We rely on the global exception handler in main.py to catch and log any DB errors
# This keeps our router code clean and the logging consistent.


# minimal ui display for main page,
# where user can just type the prompt and get the structured prompt,
# later on we can connect frontend
@router.get("/home", response_class=FileResponse)
def read_root():
    return FileResponse("static/index.html", media_type="text/html")


# route for recieving prompts
@router.post("/", status_code=status.HTTP_200_OK, response_model=PromptSchemaOutput)
def create_new_prompt(
    db: Session = Depends(get_db), prompt_data: PromptSchema = None
) -> PromptSchemaOutput:
    # process the prompt here, and create dependency current_user, to keep track of users.
    # user = get_current_user()
    # TODO: step 1 : check if the current session has user id with the request
    # step 2 : if there is no id and user has sent the prompt create user id
    # step 3 : update the user, prompt, structured_prompt tables with new information

    new_prompt = prompt_service.save_prompt(db=db, prompt_data=prompt_data)
    st_prompt = st_prompt_service.create_structured_prompt(
        session=db, prompt_data=new_prompt
    )
    return st_prompt


# NOTE: so instead of separately returning the prompt and structured prompt for this routes
# we can create schema to return all the info related to the prompt id
# since author_id is tied to the restructured prompt and non structured prompt


# If user is implemented the uncomment the below path operator
@router.get("/", status_code=status.HTTP_200_OK, response_model=List[PromptSchema])
# @router.get("/", status_code=status.HTTP_200_OK)
def get_all_previous_prompts(db: Session = Depends(get_db)):
    # get historical prompts
    # TODO: this requeires user id  dependency to retrieve the desired prompt
    # later implement user based retreival , something prompts for the current user onl.
    all_previous_prompts = prompt_service.get_all_prompt(db=db)
    return all_previous_prompts


@router.get("/{prompt_id}", status_code=status.HTTP_200_OK, response_model=PromptSchema)
def get_all_previous_prompt_by_id(prompt_id: str, db: Session = Depends(get_db)):
    # get historical prompts
    # TODO: this requeires user id  dependency to retrieve the desired prompt
    # later implement user based retreival , something prompts for the current user onl.
    all_previous_prompts = prompt_service.get_all_prompt_by_id(
        prompt_id=prompt_id, db=db
    )
    return all_previous_prompts


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(prompt_id: str, db: Session = Depends(get_db)):
    # NOTE: this requires user id to operate
    prompt_service.delete_prompt(prompt_id=prompt_id, db=db)
    pass


@router.post("/{prompt_id}", status_code=status.HTTP_200_OK)
def update_prompt(prompt_id: str, db: Session = Depends(get_db)):
    # NOTE: this also requires user id to operate
    pass
