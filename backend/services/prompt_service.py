from sqlalchemy.orm import Session
from database.models import User, PromptResults
from prompt_engine import PromptEngine, improve_prompt
from typing import List, Optional
import json

class PromptService:
    def __init__(self, db: Session, user_id: str):
       self.db = db
       self.user_id = user_id

    def save_prompt_result(self, original_prompt: str, improved_prompt: str, total_iterations: int):
        pass

    def get_user_prompt_history(self):
        pass

    def get_prompt_by_id(self, prompt_id: str):
        pass

    def delete_prompt(self, prompt_id: str):
        pass

    async def improve_and_save_prompt(self, prompt_request: dict):
        pass

    def update_user_stats(self):
        pass