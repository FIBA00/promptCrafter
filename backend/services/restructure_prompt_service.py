from sqlalchemy.orm import Session
from schema.schemas import PromptSchema, PromptSchemaOutput

from utility.logger import get_logger

lg = get_logger(__file__)


class RestructuredPromptService:
    def create_structured_prompt(self, session: Session, prompt_data: PromptSchema):
        st_prompt: str = None
        # TODO: Migrate the database driver to async because this method alone requires async job.
        # HOW TO STRUCUTRE PROMPT
        # Step 1 :
        # using option 1: regular function to rearrange the prompt data and insert into template and return string.
        # st_prompt = create_prompt_normal_way(prompt_data) this method calls two functions and return object of StructurePromptSchema which has normal and natural prompt.
        # using option 2: for more advanced option pass the generated simple template to ai and return refined and restructured prompt.
        # st_prompt = create_prompt_using_ai(prompt_data)
        self.save_structured_prompt(structured_prompt=st_prompt, session=session)
        st_prompt = self.create_prompt_normal_way(prompt_data=prompt_data)

        return st_prompt

    def get_all_restructured_prompt(self, session: Session):
        lg.debug("Getting all the restructured prompts.")
        return None

    def get_all_restructured_prompt_by_user_id(self, id: str, session: Session):
        lg.debug("Getting all the restructured prompts.")
        return None

    def get_one_structured_prompt_by_user_id(self, id: str, session: Session):
        lg.debug("Getting all the restructured prompts.")
        return None

    def save_structured_prompt(
        self, structured_prompt: dict[str, any], session: Session
    ):
        lg.debug("Getting all the restructured prompts.")
        return True

    def delete_structured_prompt(self, structured_prompt_id: str, session: Session):
        lg.debug("Getting all the restructured prompts.")
        return None

    def update_structured_prompt(self, structured_prompt_id: str, session: Session):
        lg.debug("Getting all the restructured prompts.")
        return None

    def delete_all_structured_prompt(self, user_id: str, session: Session):
        lg.debug("Getting all the restructured prompts.")
        return None

    def create_prompt_normal_way(self, prompt_data: PromptSchema) -> PromptSchemaOutput:
        """
        Functional template rendering of prompts into standard format.
        """
        role = prompt_data.role
        task = prompt_data.task
        constraints = prompt_data.constraints
        output = prompt_data.output
        personality = prompt_data.personality

        structured = self.build_structured_prompt(
            role=role,
            task=task,
            constraints=constraints,
            output=output,
            personality=personality,
        )
        natural = self.build_natural_prompt(
            role=role,
            task=task,
            constraints=constraints,
            output=output,
            personality=personality,
        )
        return PromptSchemaOutput(structured_prompt=structured, natural_prompt=natural)

    def create_prompt_using_ai(self, prompt_data: PromptSchema) -> PromptSchemaOutput:
        """
        In our case we use OllamaClient to test the functionality of the system, by sending our prompt and returning the structured and natural sounding prompt!.
        """
        # TODO: Implement ai based feature
        # build_prompt_for_ollama
        # import ollam client,
        # select model
        # call the api and pass our data and prompt for ollma also
        # it needs custom response handling this is advaced feature
        #  return PromptSchemaOutput(structured_prompt=structured, natural_prompt=natural)
        pass

    def build_structured_prompt(self, role, task, constraints, output, personality):
        return f"""
    [1. ROLE or CONTEXTUAL SETTING]: Imagine you are a {role}.

    [2. OBJECTIVE or TASK]: I want you to help me {task}.
create_prompt_using_ai
    [3. CONSTRAINTS & RESOURCES]: Here’s what I already have / can't do / must consider:
    {constraints}

    [4. PREFERRED OUTPUT STYLE]: I want the response to be in {output}.

    [5. BONUS – PERSONAL TOUCH]: Think like {personality}.
    """.strip()

    def build_natural_prompt(self, role, task, constraints, output, personality):
        return f"""
    Imagine you are {role}.
    I want you to help me {task}.
    Constraints: {constraints}
    Output: {output}
    Act like {personality}.
    """.strip()
