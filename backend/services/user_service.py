from sqlalchemy.orm import Session
from database.models import User
from auth.jwt_handler import hash_password, verify_password, create_access_token
from typing import Optional
from datetime import datetime

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, email: str, password: str) -> User:
        """Register a new user"""
        if self.get_user_by_email(email):
            raise ValueError("Email already registered")
        
        hashed_password = hash_password(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            created_at=datetime.utcnow()
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    def login_user(self, email: str, password: str) -> dict:
        user = self.authenticate_user(email, password)
        if not user:
            raise ValueError("Invalid email or password")
        
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        access_token = create_access_token(data={"sub": user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "total_prompts": user.total_prompts,
                "total_jobs": user.total_jobs
            }
        }