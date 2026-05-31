import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.models.document import Document
from app.models.chunk import Chunk
from app.services.parser import extract_text, segment_clauses
from app.services.embedding_provider import get_embedding_provider
from app.core.config import settings

router = APIRouter()

def process_document(db: Session, doc_id: int, file_bytes: bytes, filename: str):
    try:
        # Extract text
        text = extract_text(file_bytes, filename)
        
        # Segment into clauses
        chunks = segment_clauses(text)
        
        # Get embeddings and save
        embedding_provider = get_embedding_provider(
            settings.EMBEDDING_PROVIDER, 
            settings.EMBEDDING_API_KEY or "dummy"
        )
        
        for chunk in chunks:
            # Embed text (mocking if no key)
            try:
                embedding = embedding_provider.get_embedding(chunk.text)
            except Exception:
                # Fallback zero vector if no key/provider fails
                embedding = [0.0] * 1536
                
            db_chunk = Chunk(
                document_id=doc_id,
                text=chunk.text,
                char_start=chunk.char_start,
                char_end=chunk.char_end,
                clause_type=chunk.clause_type,
                embedding=embedding
            )
            db.add(db_chunk)
            
        db_doc = db.query(Document).filter(Document.id == doc_id).first()
        if db_doc:
            db_doc.status = "processed"
            
        db.commit()
    except Exception as e:
        db_doc = db.query(Document).filter(Document.id == doc_id).first()
        if db_doc:
            db_doc.status = "error"
            db.commit()
        print(f"Error processing doc {doc_id}: {e}")

@router.post("/", response_model=dict)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    if not file.filename.lower().endswith(('.pdf', '.docx', '.txt')):
        raise HTTPException(status_code=400, detail="Invalid file type")
        
    contents = await file.read()
    
    # Save to disk
    os.makedirs("data/uploads", exist_ok=True)
    file_path = os.path.join("data/uploads", file.filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Save document record
    db_doc = Document(
        org_id=current_user.org_id,
        filename=file.filename,
        type=file.filename.split('.')[-1],
        status="processing",
        uploaded_by=current_user.id
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # Process in background
    background_tasks.add_task(process_document, db, db_doc.id, contents, file.filename)
    
    return {"id": db_doc.id, "filename": db_doc.filename, "status": db_doc.status}

@router.get("/")
def list_documents(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # In a real app, filter by org_id
    docs = db.query(Document).all()
    return [{"id": d.id, "filename": d.filename, "status": d.status, "created_at": d.created_at} for d in docs]
