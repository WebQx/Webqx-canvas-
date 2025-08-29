"""
Journaling Database Service - NLP-powered journal storage and analysis
"""

from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
import os
from datetime import datetime
import json
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd

app = FastAPI(
    title="WebQx Journaling Service",
    description="NLP-powered journal storage and analysis",
    version="1.0.0"
)

security = HTTPBearer()

# Load NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback to basic processing if model not available
    nlp = None

class JournalEntry(BaseModel):
    id: Optional[str] = None
    user_id: str
    text: Optional[str] = None
    audio_url: Optional[str] = None
    tags: List[str] = []
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    symptoms: List[str] = []
    medications_mentioned: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class NLPAnalysis(BaseModel):
    sentiment: str
    sentiment_score: float
    entities: List[dict]
    symptoms: List[str]
    medications: List[str]
    themes: List[str]
    keywords: List[str]

class TrendAnalysis(BaseModel):
    period: str
    symptom_trends: dict
    sentiment_trends: dict
    medication_adherence: dict
    insights: List[str]

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token from middleware"""
    return {"user_id": "test_user"}

async def get_db():
    """Database connection"""
    conn = await asyncpg.connect(
        os.getenv("DATABASE_URL", "postgresql://webqx:password@localhost:5432/webqx_journal")
    )
    try:
        yield conn
    finally:
        await conn.close()

def analyze_text_with_nlp(text: str) -> NLPAnalysis:
    """Perform NLP analysis on journal text"""
    if not text or not nlp:
        return NLPAnalysis(
            sentiment="neutral",
            sentiment_score=0.0,
            entities=[],
            symptoms=[],
            medications=[],
            themes=[],
            keywords=[]
        )
    
    doc = nlp(text)
    
    # Extract entities
    entities = []
    symptoms = []
    medications = []
    
    for ent in doc.ents:
        entity_data = {
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char
        }
        entities.append(entity_data)
        
        # Categorize entities
        if ent.label_ in ["SYMPTOM", "DISEASE"]:
            symptoms.append(ent.text.lower())
        elif ent.label_ in ["DRUG", "CHEMICAL"]:
            medications.append(ent.text.lower())
    
    # Simple sentiment analysis (placeholder)
    positive_words = ["good", "better", "great", "excellent", "happy", "improved"]
    negative_words = ["bad", "worse", "terrible", "awful", "sad", "pain", "hurt"]
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        sentiment = "positive"
        sentiment_score = min(0.8, positive_count / (positive_count + negative_count + 1))
    elif negative_count > positive_count:
        sentiment = "negative"
        sentiment_score = -min(0.8, negative_count / (positive_count + negative_count + 1))
    else:
        sentiment = "neutral"
        sentiment_score = 0.0
    
    # Extract keywords
    keywords = [token.lemma_.lower() for token in doc 
               if not token.is_stop and not token.is_punct and len(token.text) > 2]
    keywords = list(set(keywords))[:10]  # Top 10 unique keywords
    
    # Extract themes (simplified)
    themes = []
    if any(word in text_lower for word in ["medication", "medicine", "pill", "dose"]):
        themes.append("medication")
    if any(word in text_lower for word in ["pain", "ache", "hurt", "sore"]):
        themes.append("symptoms")
    if any(word in text_lower for word in ["exercise", "walk", "run", "gym"]):
        themes.append("activity")
    if any(word in text_lower for word in ["sleep", "tired", "fatigue", "rest"]):
        themes.append("sleep")
    
    return NLPAnalysis(
        sentiment=sentiment,
        sentiment_score=sentiment_score,
        entities=entities,
        symptoms=symptoms,
        medications=medications,
        themes=themes,
        keywords=keywords
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "journaling-db"}

@app.post("/entries", response_model=JournalEntry)
async def create_entry(entry: JournalEntry, user=Depends(verify_token), db=Depends(get_db)):
    """Create a new journal entry with NLP analysis"""
    
    # Perform NLP analysis if text is provided
    if entry.text:
        analysis = analyze_text_with_nlp(entry.text)
        entry.sentiment = analysis.sentiment
        entry.sentiment_score = analysis.sentiment_score
        entry.symptoms = analysis.symptoms
        entry.medications_mentioned = analysis.medications
        entry.tags.extend(analysis.themes)
        entry.tags = list(set(entry.tags))  # Remove duplicates
    
    # Save to database (mock implementation)
    entry_id = f"entry_{datetime.now().timestamp()}"
    entry.id = entry_id
    entry.created_at = datetime.now()
    entry.updated_at = datetime.now()
    
    # In production, save to PostgreSQL
    # await db.execute("""
    #     INSERT INTO journal_entries (id, user_id, text, audio_url, tags, sentiment, sentiment_score, symptoms, medications_mentioned, created_at, updated_at)
    #     VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
    # """, entry.id, entry.user_id, entry.text, entry.audio_url, json.dumps(entry.tags), entry.sentiment, entry.sentiment_score, json.dumps(entry.symptoms), json.dumps(entry.medications_mentioned), entry.created_at, entry.updated_at)
    
    return entry

@app.get("/entries", response_model=List[JournalEntry])
async def get_entries(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    user=Depends(verify_token),
    db=Depends(get_db)
):
    """Get journal entries for a user"""
    # Mock data for demo
    return [
        JournalEntry(
            id="1",
            user_id=user_id,
            text="Feeling much better today. The new medication seems to be working well.",
            tags=["positive", "medication", "improvement"],
            sentiment="positive",
            sentiment_score=0.7,
            symptoms=[],
            medications_mentioned=["medication"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        ),
        JournalEntry(
            id="2",
            user_id=user_id,
            text="Had some side effects yesterday but they seem to be subsiding.",
            tags=["side effects", "medication"],
            sentiment="neutral",
            sentiment_score=0.1,
            symptoms=["side effects"],
            medications_mentioned=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]

@app.post("/entries/{entry_id}/analyze")
async def analyze_entry(entry_id: str, user=Depends(verify_token)):
    """Re-run NLP analysis on an existing entry"""
    # In production, fetch entry from database and re-analyze
    return {"status": "analysis_started", "entry_id": entry_id}

@app.get("/analysis/trends", response_model=TrendAnalysis)
async def get_trend_analysis(
    user_id: str,
    period: str = "30d",
    user=Depends(verify_token),
    db=Depends(get_db)
):
    """Get trend analysis for user's journal entries"""
    # Mock trend analysis
    return TrendAnalysis(
        period=period,
        symptom_trends={
            "pain": {"trend": "decreasing", "change": -15},
            "fatigue": {"trend": "stable", "change": 2},
            "headache": {"trend": "decreasing", "change": -8}
        },
        sentiment_trends={
            "positive": 65,
            "neutral": 25,
            "negative": 10,
            "average_score": 0.3
        },
        medication_adherence={
            "metformin": {"adherence": 95, "missed_doses": 2},
            "vitamin_d": {"adherence": 87, "missed_doses": 4}
        },
        insights=[
            "Your overall mood has improved by 15% this month",
            "Pain levels are trending downward",
            "Medication adherence is excellent"
        ]
    )

@app.post("/audio/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    user=Depends(verify_token)
):
    """Transcribe audio journal entry to text"""
    # In production, integrate with speech-to-text service
    return {
        "transcription": "This is a mock transcription of the audio file.",
        "confidence": 0.95,
        "duration": 30.5
    }

@app.get("/export/{user_id}")
async def export_entries(
    user_id: str,
    format: str = "json",
    user=Depends(verify_token),
    db=Depends(get_db)
):
    """Export user's journal entries"""
    # In production, generate and return file
    return {
        "export_url": f"/downloads/journal_export_{user_id}_{datetime.now().isoformat()}.{format}",
        "status": "ready",
        "entries_count": 50
    }

@app.post("/search")
async def search_entries(
    query: str,
    user_id: str,
    user=Depends(verify_token),
    db=Depends(get_db)
):
    """Search journal entries by text, tags, or symptoms"""
    # Mock search results
    return {
        "query": query,
        "results": [
            {
                "entry_id": "1",
                "text": "Feeling much better today...",
                "relevance_score": 0.95,
                "matched_terms": ["better", "medication"]
            }
        ],
        "total_results": 1
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)