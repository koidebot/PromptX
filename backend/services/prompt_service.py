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
        res = PromptResults(
            user_id=self.user_id,
            original_prompt=original_prompt,
            improved_prompt=improved_prompt,
            total_iterations=total_iterations
        )
        self.db.add(res)
        self.db.commit()
        return res

    def get_user_prompt_history(self, limit: int=50):
        return self.db.query(PromptResults).filter(PromptResults.user_id == self.user_id).order_by(PromptResults.created_at.desc()).limit(limit).all()

    def get_prompt_by_id(self, prompt_id: str):
        return (self.db.query(PromptResults)
              .filter(PromptResults.id == prompt_id,
                     PromptResults.user_id == self.user_id)
              .first())

    def delete_prompt(self, prompt_id: str):
        self.db.query(PromptResults.filter(PromptResults.id == prompt_id).delete())
        self.db.commit()

    async def improve_and_save_prompt(self, prompt_request: dict):
        try:
            result = await improve_prompt(prompt_request)
            if result['status'] == 'completed':
                prompt_result = self.save_prompt_result(
                    original_prompt=prompt_request['prompt'],
                    improved_prompt=result['final_prompt'],
                    total_iterations=result['total_iterations']
                )
                return {
                  "status": "completed",
                  "prompt_id": prompt_result.id,
                  "original_prompt": prompt_result.original_prompt,
                  "improved_prompt": prompt_result.improved_prompt,
                  "total_iterations": prompt_result.total_iterations,
                  "created_at": prompt_result.created_at
              }
            else:
                return result
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    def update_user_stats(self):
        user = self.db.query(User).filter(User.id == self.user_id).first()
        if user:
            user.total_prompts += 1
            self.db.commit()
            return user
        return None