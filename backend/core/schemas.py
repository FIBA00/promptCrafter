from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
import uuid

# TODO: Revert to EmailStr when email-validator is installed
# from pydantic import EmailStr
EmailStr = str


class PromptSchema(BaseModel):
    # so this is basically just a data model for a prompt request from user
    # Optional fields for input (the user might just send 'task' initially)
    prompt_id: Optional[uuid.UUID] = None
    author_id: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None

    # the prompt
    title: Optional[str]
    role: Optional[str]
    task: Optional[str]
    output: Optional[str]
    tags: List[str] = []
    constraints: Optional[str] = None
    personality: Optional[str] = None

    class Config:
        from_attributes = True


class PromptSchemaOutput(BaseModel):
    # so this is the response schema for our modified prompt
    structured_prompt: str
    natural_prompt: str
    # we need to return the prompt id and author id to link the prompt and structured prompt together, but from the PromptSchema
    details: PromptSchema

    class Config:
        from_attributes = True


class UserPromptsSchema(PromptSchema):
    st_prompts: List[PromptSchema]

    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    email: str
    password: str


class UserLoginSchema(BaseModel):
    email: str
    password: str


class UserOutSchema(BaseModel):
    user_id: uuid.UUID
    email: str
    created_at: datetime
    is_admin: bool
    is_verified: bool

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    user_id: Optional[str] = None
    is_admin: bool = False
    is_verified: bool = False


class TokenOutSchema(BaseModel):
    access_token: str
    token_type: str


class EmailModel(BaseModel):
    emails: List[EmailStr]
