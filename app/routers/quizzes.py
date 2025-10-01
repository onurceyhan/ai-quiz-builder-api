from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

from app.database import get_db
from app.models import User, Quiz, Question
from app.schemas import (
    QuizCreate, QuizUpdate, Quiz as QuizSchema, QuizSummary,
    QuizGenerationRequest, QuizListResponse, Message
)
from app.auth import get_current_active_user

load_dotenv()

router = APIRouter()

# LangChain + Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_gemini_llm():
    """Get LangChain Gemini LLM instance"""
    if not GEMINI_API_KEY:
        return None
    
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.7
    )

def generate_quiz_with_ai(
    title: str, 
    prompt: str, 
    question_count: int, 
    difficulty: str,
    category: str = None
) -> List[dict]:
    """Generate quiz questions using LangChain + Gemini."""
    
    llm = get_gemini_llm()
    if not llm:
        # Fallback to sample questions if Gemini is not configured
        return generate_sample_questions(question_count, title)
    
    difficulty_instructions = {
        "easy": "kolay seviyede, temel bilgi gerektiren",
        "medium": "orta seviyede, analiz gerektiren", 
        "hard": "zor seviyede, derin düşünme gerektiren"
    }
    
    system_content = f"""Sen uzman bir quiz oluşturucususun. Verilen konuda {difficulty_instructions.get(difficulty, 'orta seviyede')} çoktan seçmeli sorular hazırlarsın.

KURALLAR:
- Her soru için 4 seçenek (A, B, C, D) oluştur
- Sadece bir doğru cevap olsun
- Yanıltıcı ama mantıklı seçenekler ekle
- Soruları açık ve anlaşılır yaz
- Türkçe dilbilgisi kurallarına uy

ÇIKTI FORMATI (SADECE JSON):
{{
  "questions": [
    {{
      "text": "Soru metni burada",
      "options": ["Seçenek A", "Seçenek B", "Seçenek C", "Seçenek D"],
      "correct": 0
    }}
  ]
}}"""

    user_content = f"""GÖREV: {question_count} adet çoktan seçmeli soru oluştur

KONU: {title}
AÇIKLAMA: {prompt}
ZORLUİK: {difficulty}
{f'KATEGORİ: {category}' if category else ''}

Lütfen yukarıdaki JSON formatında tam olarak {question_count} adet soru oluştur."""

    try:
        # Gemini için sistem mesajını kullanıcı mesajıyla birleştiriyoruz
        combined_content = f"{system_content}\n\n{user_content}"
        messages = [HumanMessage(content=combined_content)]
        
        response = llm.invoke(messages)
        content = response.content
        
        # JSON içeriğini temizle ve parse et
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        quiz_data = json.loads(content)
        questions = quiz_data.get("questions", [])
        
        # Eğer yeterli soru yoksa, eksikleri sample ile tamamla
        if len(questions) < question_count:
            remaining = question_count - len(questions)
            sample_questions = generate_sample_questions(remaining, title)
            questions.extend(sample_questions)
        
        return questions[:question_count]  # Sadece istenen sayıda soru döndür
        
    except Exception as e:
        print(f"Gemini AI generation error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Gemini API'den gelen specific hatalar
        if "quota" in str(e).lower() or "limit" in str(e).lower():
            print("Gemini API quota exceeded, using sample questions")
        elif "key" in str(e).lower() or "auth" in str(e).lower():
            print("Gemini API authentication error, using sample questions")
        else:
            print("General Gemini error, using sample questions")
            
        # Fallback to sample questions if AI generation fails
        return generate_sample_questions(question_count, title)

def generate_sample_questions(count: int, title: str) -> List[dict]:
    """Generate sample questions when AI is not available."""
    print(f"Generating {count} sample questions for topic: {title}")
    
    # Konu bazlı sample sorular
    sample_templates = {
        "matematik": [
            "2x + 5 = 15 denkleminde x'in değeri nedir?",
            "Bir üçgenin iç açılarının toplamı kaç derecedir?", 
            "√16 ifadesinin değeri nedir?",
            "y = 2x + 3 doğrusunun eğimi nedir?"
        ],
        "fen": [
            "Su molekülünün kimyasal formülü nedir?",
            "Işık hızı yaklaşık olarak saniyede kaç kilometre?",
            "Atomun çekirdeğinde hangi parçacıklar bulunur?",
            "Newton'un kaç hareket yasası vardır?"
        ],
        "tarih": [
            "Osmanlı İmparatorluğu hangi yılda kurulmuştur?",
            "Cumhuriyet hangi tarihte ilan edilmiştir?",
            "İstanbul'un fetih tarihi nedir?",
            "Atatürk hangi şehirde doğmuştur?"
        ]
    }
    
    # Başlığa göre uygun soruları seç
    title_lower = title.lower()
    template_questions = []
    
    if any(word in title_lower for word in ["matematik", "mat", "hesap", "sayı"]):
        template_questions = sample_templates["matematik"]
    elif any(word in title_lower for word in ["fen", "fizik", "kimya", "biyoloji"]):
        template_questions = sample_templates["fen"] 
    elif any(word in title_lower for word in ["tarih", "cumhuriyet", "osmanlı"]):
        template_questions = sample_templates["tarih"]
    
    questions = []
    for i in range(count):
        if template_questions and i < len(template_questions):
            text = template_questions[i]
            # Konuya uygun seçenekler
            if "matematik" in title_lower:
                options = ["5", "3", "10", "7"] if "2x + 5" in text else ["180°", "90°", "360°", "270°"]
                correct = 0 if "2x + 5" in text else 0
            else:
                options = ["Seçenek A", "Seçenek B", "Seçenek C", "Seçenek D"] 
                correct = 0
        else:
            text = f"{title} konusu ile ilgili {i + 1}. soru. Bu soruyu düzenleyerek kendi sorunuzu yazabilirsiniz."
            options = ["Seçenek A", "Seçenek B", "Seçenek C", "Seçenek D"]
            correct = 0
            
        questions.append({
            "text": text,
            "options": options,
            "correct": correct
        })
    
    return questions

@router.post("/", response_model=QuizSchema)
async def create_quiz(
    quiz_data: QuizCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new quiz with AI-generated questions."""
    
    # Create quiz
    db_quiz = Quiz(
        title=quiz_data.title,
        prompt=quiz_data.prompt,
        category=quiz_data.category,
        difficulty=quiz_data.difficulty,
        owner_id=current_user.id
    )
    
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    # Generate questions with AI
    questions_data = generate_quiz_with_ai(
        quiz_data.title,
        quiz_data.prompt,
        quiz_data.question_count,
        quiz_data.difficulty,
        quiz_data.category
    )
    
    # Save questions to database
    for order, question_data in enumerate(questions_data):
        db_question = Question(
            quiz_id=db_quiz.id,
            text=question_data["text"],
            options=question_data["options"],
            correct=question_data["correct"],
            order=order
        )
        db.add(db_question)
    
    db.commit()
    db.refresh(db_quiz)
    
    return db_quiz

@router.post("/generate", response_model=QuizSchema)
async def generate_quiz(
    generation_request: QuizGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a quiz using AI based on the request."""
    
    # Create quiz
    db_quiz = Quiz(
        title=generation_request.title,
        prompt=generation_request.prompt,
        category=generation_request.category,
        difficulty=generation_request.difficulty,
        owner_id=current_user.id
    )
    
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    # Generate questions with AI
    questions_data = generate_quiz_with_ai(
        generation_request.title,
        generation_request.prompt,
        generation_request.question_count,
        generation_request.difficulty,
        generation_request.category
    )
    
    # Save questions to database
    for order, question_data in enumerate(questions_data):
        db_question = Question(
            quiz_id=db_quiz.id,
            text=question_data["text"],
            options=question_data["options"],
            correct=question_data["correct"],
            order=order
        )
        db.add(db_question)
    
    db.commit()
    db.refresh(db_quiz)
    
    return db_quiz

@router.get("/", response_model=QuizListResponse)
async def get_user_quizzes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """Get all quizzes for the current user."""
    
    # Eager load questions ile quiz'leri çek
    from sqlalchemy.orm import joinedload
    
    quizzes = db.query(Quiz).options(
        joinedload(Quiz.questions)
    ).filter(
        Quiz.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    print(f"Found {len(quizzes)} quizzes for user {current_user.id}")
    
    # Convert to summary format with question count
    quiz_summaries = []
    for quiz in quizzes:
        question_count = len(quiz.questions) if quiz.questions else 0
        print(f"Quiz {quiz.id} '{quiz.title}' has {question_count} questions")
        
        quiz_summary = QuizSummary(
            id=quiz.id,
            title=quiz.title,
            prompt=quiz.prompt,
            category=quiz.category,
            difficulty=quiz.difficulty,
            owner_id=quiz.owner_id,
            created_at=quiz.created_at,
            question_count=question_count
        )
        quiz_summaries.append(quiz_summary)
    
    print(f"Returning {len(quiz_summaries)} quiz summaries")
    
    total = db.query(Quiz).filter(Quiz.owner_id == current_user.id).count()
    
    return QuizListResponse(quizzes=quiz_summaries, total=total)

@router.get("/{quiz_id}", response_model=QuizSchema)
async def get_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific quiz with all questions."""
    
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.owner_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    return quiz

@router.put("/{quiz_id}", response_model=QuizSchema)
async def update_quiz(
    quiz_id: int,
    quiz_update: QuizUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a quiz and its questions."""
    
    # Get quiz
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.owner_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Update quiz fields
    quiz.title = quiz_update.title
    quiz.prompt = quiz_update.prompt
    quiz.category = quiz_update.category
    quiz.difficulty = quiz_update.difficulty
    
    # Update questions if provided
    if quiz_update.questions is not None:
        # Delete existing questions
        db.query(Question).filter(Question.quiz_id == quiz_id).delete()
        
        # Add new questions
        for order, question_data in enumerate(quiz_update.questions):
            db_question = Question(
                quiz_id=quiz_id,
                text=question_data.text,
                options=question_data.options,
                correct=question_data.correct,
                order=question_data.order if question_data.order is not None else order
            )
            db.add(db_question)
    
    db.commit()
    db.refresh(quiz)
    
    return quiz

@router.delete("/{quiz_id}", response_model=Message)
async def delete_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a quiz and all its questions."""
    
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.owner_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    db.delete(quiz)
    db.commit()
    
    return {"message": "Quiz deleted successfully"} 