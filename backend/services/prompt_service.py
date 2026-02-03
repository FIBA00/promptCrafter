import uuid
from sqlalchemy.orm import Session
from core.models import Prompts
from schema.schemas import PromptSchema
from utility.logger import get_logger

lg = get_logger(__file__)


class PromptService:
    def get_all_prompt(self, session: Session):
        lg.debug("Getting all the prompts.")
        return None

    # We need to get current user from the browser
    # if the browser didnt sent us id we have to assign new author id.
    def save_prompt(
        self,
        session: Session,
        prompt_data: PromptSchema,
        author_id: str = None,
    ):
        prompt_data_dict = prompt_data.model_dump()

        # We must use the SQLAlchemy Model (Prompts), not the Pydantic Schema
        if not prompt_data_dict.get("prompt_id"):
            prompt_data_dict["prompt_id"] = str(uuid.uuid4())

        new_prompt = Prompts(**prompt_data_dict)

        # new_prompt.author_id = author_id # Uncomment when author logic is ready
        lg.debug(f"Saving prompt: {new_prompt.prompt_id}")

        session.add(new_prompt)
        session.commit()
        session.refresh(new_prompt)

        # Return the Pydantic schema so the rest of the app can use it easily
        return PromptSchema.model_validate(new_prompt)

    def update_prompt(self, prompt_id: str, session: Session):
        lg.debug(f"Updating  prompt: {prompt_id}")

        return None

    def delete_prompt(self, prompt_id: str, session: Session):
        lg.debug(f"Deleting prompt: {prompt_id}")

        return None
