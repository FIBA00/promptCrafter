from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uuid


class PromptSchema(BaseModel):
    # so this is basically just a data model for a prompt request from user
    # Optional fields for input (the user might just send 'task' initially)
    prompt_id: Optional[uuid.UUID] = None
    author_id: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None
    tags: List[str] = []

    # the prompt
    title: Optional[str] = None
    role: Optional[str] = None
    task: str
    constraints: Optional[str] = None
    output: Optional[str] = None
    personality: Optional[str] = None

    class Config:
        from_attributes = True


class PromptSchemaOutput(BaseModel):
    # so this is the response schema for our modified prompt
    structured_prompt: str
    natural_prompt: str


class UserPromptsSchema(PromptSchema):
    st_prompts: List[PromptSchema]

    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    email: str
    password: str


class UserOutSchema(BaseModel):
    user_id: uuid.UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenOutSchema(BaseModel):
    access_token: str
    token_type: str
