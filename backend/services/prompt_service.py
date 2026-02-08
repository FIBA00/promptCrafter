import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


from db.models import Prompts
from core.schemas import PromptSchema
from utility.logger import get_logger
from core.custom_error_handlers import PromptNotFound

lg = get_logger(script_path=__file__)


class PromptService:
    # We need to get current user from the browser
    # if the browser didnt sent us id we have to assign new author id.
    def save_prompt(
        self,
        db: Session,
        prompt_data: PromptSchema,
        author_id: str = None,
    ):
        try:
            prompt_data_dict = prompt_data.model_dump()

            # We must use the SQLAlchemy Model (Prompts), not the Pydantic Schema
            if not prompt_data_dict.get("prompt_id"):
                prompt_data_dict["prompt_id"] = str(uuid.uuid4())

            new_prompt = Prompts(**prompt_data_dict)

            # new_prompt.author_id = author_id # Uncomment when author logic is ready
            lg.debug(f"Saving prompt: {new_prompt.prompt_id}")

            db.add(instance=new_prompt)
            db.commit()
            db.refresh(instance=new_prompt)

            # Return the Pydantic schema so the rest of the app can use it easily
            return PromptSchema.model_validate(new_prompt)

        except SQLAlchemyError as e:
            # This catches ANY database error (connection lost, constraint violation, etc.)
            db.rollback()  # CRITICAL: Reset the db so it's clean for the next request
            lg.error(f"Database Error saving prompt: {str(e)}")
            raise e  # Re-raise it so the router knows something went wrong

        except Exception as e:
            # This catches any other unexpected Python error (like a bug in our code)
            lg.error(f"Unexpected Error in save_prompt: {str(e)}")
            raise e

    def get_all_prompt(self, db: Session):
        lg.debug("Getting all the prompts.")
        try:
            all_prompts = db.query(Prompts).limit(100).all()
            if not all_prompts:
                lg.debug("Prompts table is empty - no prompts found in the database.")

            lg.info(f"Successfully retreived {len(all_prompts)} posts from database.")
            return all_prompts
        except SQLAlchemyError as e:
            # This catches ANY database error (connection lost, constraint violation, etc.)
            db.rollback()  # CRITICAL: Reset the session so it's clean for the next request
            lg.error(f"Database Error saving prompt: {str(e)}")
            raise e  # Re-raise it so the router knows something went wrong

        except Exception as e:
            # This catches any other unexpected Python error (like a bug in our code)
            lg.error(f"Unexpected Error in save_prompt: {str(e)}")
            raise e

        return None

    def get_all_prompt_by_id(self, prompt_id: str, db: Session) -> Prompts | None:
        lg.debug("Getting all the prompts.")
        try:
            prompts_by_id = (
                db.query(Prompts).filter(Prompts.prompt_id == prompt_id).first()
            )
            if not prompts_by_id:
                lg.debug("Prompt not found in the database.")
                raise PromptNotFound()

            lg.info("Successfully retrieved prompts from database.")
            return prompts_by_id
        except SQLAlchemyError as e:
            # This catches ANY database error (connection lost, constraint violation, etc.)
            db.rollback()  # CRITICAL: Reset the session so it's clean for the next request
            lg.error(f"Database Error saving prompt: {str(e)}")
            raise e  # Re-raise it so the router knows something went wrong

        except Exception as e:
            # This catches any other unexpected Python error (like a bug in our code)
            lg.error(f"Unexpected Error in save_prompt: {str(e)}")
            raise e

    def update_prompt(self, prompt_id: str, db: Session):
        lg.debug(f"Updating  prompt: {prompt_id}")

        return None

    def delete_prompt(self, prompt_id: str, db: Session) -> bool:
        lg.debug(f"Deleting prompt: {prompt_id}")

        return None
