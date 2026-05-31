from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api import deps
from app.models.user import User
from app.models.chunk import Precedent, PrecedentChunk
from app.services.embedding_provider import get_embedding_provider
from app.core.config import settings

router = APIRouter()

# Synthetic data for demo purposes
SYNTHETIC_PRECEDENTS = [
    {
        "filename": "synthetic_nda_1.txt",
        "clauses": [
            {"text": "The Receiving Party shall not disclose the Confidential Information to any third party without prior written consent.", "type": "Confidentiality"},
            {"text": "This Agreement shall be governed by the laws of the State of Delaware.", "type": "Governing Law"}
        ]
    },
    {
        "filename": "synthetic_msa_1.txt",
        "clauses": [
            {"text": "Supplier's total liability under this Agreement shall not exceed the total fees paid by Customer in the 12 months preceding the claim.", "type": "Limitation of Liability"},
            {"text": "Either party may terminate this Agreement for convenience upon 30 days written notice.", "type": "Termination"}
        ]
    }
]

def generate_synthetic_precedents(db: Session, org_id: int):
    embedding_provider = get_embedding_provider(
        settings.EMBEDDING_PROVIDER, 
        settings.EMBEDDING_API_KEY or "dummy"
    )
    
    for prec_data in SYNTHETIC_PRECEDENTS:
        # Check if exists
        existing = db.query(Precedent).filter(Precedent.filename == prec_data["filename"]).first()
        if existing:
            continue
            
        precedent = Precedent(org_id=org_id, filename=prec_data["filename"])
        db.add(precedent)
        db.commit()
        db.refresh(precedent)
        
        for clause in prec_data["clauses"]:
            try:
                embedding = embedding_provider.get_embedding(clause["text"])
            except Exception:
                embedding = [0.0] * 1536
                
            p_chunk = PrecedentChunk(
                precedent_id=precedent.id,
                text=clause["text"],
                clause_type=clause["type"],
                embedding=embedding
            )
            db.add(p_chunk)
        db.commit()

@router.post("/generate-synthetic")
def trigger_synthetic_generation(
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_admin)
):
    background_tasks.add_task(generate_synthetic_precedents, db, current_user.org_id)
    return {"message": "Synthetic precedent generation started in background"}

@router.get("/")
def list_precedents(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_admin)
):
    precedents = db.query(Precedent).all()
    return precedents

def retrieve_similar_precedents(db: Session, query_embedding: list, clause_type: str = None, top_k: int = 3):
    # Uses pgvector's cosine distance operator <=>
    # Requires vector extension to be enabled in DB
    
    # We will use SQLAlchemy's text() for raw SQL to make it simpler with pgvector
    # Or use pgvector.sqlalchemy Vector type methods
    
    base_query = db.query(PrecedentChunk)
    if clause_type:
        base_query = base_query.filter(PrecedentChunk.clause_type == clause_type)
        
    results = base_query.order_by(
        PrecedentChunk.embedding.cosine_distance(query_embedding)
    ).limit(top_k).all()
    
    return [r.text for r in results]
