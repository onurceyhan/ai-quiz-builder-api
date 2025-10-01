from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleAuth(BaseModel):
    token: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Question Schemas
class QuestionBase(BaseModel):
    text: str
    options: List[str]
    correct: int

class QuestionCreate(QuestionBase):
    order: Optional[int] = 0

class QuestionUpdate(QuestionBase):
    order: Optional[int] = None

class Question(QuestionBase):
    id: int
    quiz_id: int
    order: int
    created_at: datetime

    class Config:
        from_attributes = True

# Quiz Schemas
class QuizBase(BaseModel):
    title: str
    prompt: str
    category: Optional[str] = None
    difficulty: str = "medium"

class QuizCreate(QuizBase):
    question_count: Optional[int] = 10

class QuizUpdate(QuizBase):
    questions: Optional[List[QuestionUpdate]] = None

class Quiz(QuizBase):
    id: int
    owner_id: int
    created_at: datetime
    questions: List[Question] = []

    class Config:
        from_attributes = True

class QuizSummary(QuizBase):
    id: int
    owner_id: int
    created_at: datetime
    question_count: int

    class Config:
        from_attributes = True

# AI Generation Schemas
class QuizGenerationRequest(BaseModel):
    title: str
    prompt: str
    question_count: int = 10
    difficulty: str = "medium"
    category: Optional[str] = None

# Response Schemas
class Message(BaseModel):
    message: str

class QuizListResponse(BaseModel):
    quizzes: List[QuizSummary]
    total: int 