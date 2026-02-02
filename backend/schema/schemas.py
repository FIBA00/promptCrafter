from pydantic import BaseModel
from datetime import datetime, date 
import uuid 


class PromptSchema(BaseModel):
    # so this is basically just a data model for a prompt request from user
    """should match this form when sent
    {
		"prompt_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
		"title": "Create a Python Script",
		"role": "Python Developer",
		"task": "Write a script to scrape data from a website",
		"constraints": "Use Beautiful Soup and Requests libraries",
		"output": "Python script file (.py)",
		"personality": "Helpful and concise",
		"created_at": "2023-10-27T10:00:00Z",
		"tags": ["python", "scraping", "web"],
		"author": "user123"
	}

    """
    prompt_id: uuid.UUID 
    title: str 
    role: str
    task: str
    constraints: str
    output: str
    personality: str
    created_at: datetime
    tags: list[str] = []
    author: str


class PromptSchemaOutput(BaseModel):
    # so this is the response schema for our modified prompt
    structured_prompt: str
    natural_prompt: str