from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database.connections import Base
import uuid
from datetime import datetime, timezone

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    created_at = Column(DateTime)
    last_login = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    total_prompts = Column(Integer, default=0)
    total_jobs = Column(Integer, default=0)

    prompt_results = relationship("PromptResults", back_populates="user")

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"
    
class PromptResults(Base):
    __tablename__ = 'prompt_results'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)

    original_prompt = Column(Text, nullable=False)
    improved_prompt = Column(Text, nullable=False)
    total_iterations = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="prompt_results")

    def __repr__(self):
        return f"<PromptResults(id='{self.id}', user_id='{self.user_id}')>"