from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableList

from db.database import Base


class Prompts(Base):
    """should match this
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
    """

    __tablename__ = "prompts"

    prompt_id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    role = Column(String, index=True)
    task = Column(String, index=True)
    constraints = Column(String)
    output = Column(String)
    personality = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tags = Column(MutableList.as_mutable(String), default=[])
    author = relationship("User", back_populates="prompts")


class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    prompts = relationship("Prompts", back_populates="author")
