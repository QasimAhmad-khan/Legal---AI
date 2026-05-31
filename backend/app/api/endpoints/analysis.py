import json
import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.models.document import Document
from app.models.chunk import Chunk
from app.models.analysis import Analysis, ComplianceRule, AuditLog
from app.api.endpoints.precedents import retrieve_similar_precedents
from app.services.llm_provider import get_llm_provider
from app.core.config import settings

router = APIRouter()

@router.post("/{doc_id}/analyze")
async def analyze_document(
    doc_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # Verify doc
    doc = db.query(Document).filter(Document.id == doc_id, Document.org_id == current_user.org_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if doc.status != "processed":
        raise HTTPException(status_code=400, detail="Document parsing not finished")

    chunks = db.query(Chunk).filter(Chunk.document_id == doc_id).all()
    compliance_rules = [r.text for r in db.query(ComplianceRule).filter(ComplianceRule.org_id == current_user.org_id, ComplianceRule.active == True).all()]
    
    llm = get_llm_provider(settings.LLM_PROVIDER, settings.LLM_API_KEY or "dummy")

    async def stream_analysis():
        results = []
        for i, chunk in enumerate(chunks):
            yield f"data: {json.dumps({'status': 'processing', 'chunk': i+1, 'total': len(chunks)})}\n\n"
            
            try:
                # 1. Retrieve Precedents
                precedents = retrieve_similar_precedents(db, chunk.embedding, top_k=2)
                
                # 2. Analyze
                res = llm.analyze_clause(chunk.text, precedents, compliance_rules)
                
                chunk_result = {
                    "text": chunk.text,
                    "summary": res.summary,
                    "risk_score": res.risk_score,
                    "compliance_verdict": res.compliance_verdict
                }
                results.append(chunk_result)
                yield f"data: {json.dumps({'status': 'result', 'data': chunk_result})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
                
        # 3. Store Results
        analysis = Analysis(
            document_id=doc_id,
            summary_json=results,
            risk_json={"overall": "calculated from results"},
            compliance_json={"rules_checked": len(compliance_rules)},
            model_used=settings.LLM_PROVIDER
        )
        db.add(analysis)
        
        audit = AuditLog(
            user_id=current_user.id,
            action="analyze_document",
            payload={"doc_id": doc_id, "chunks_analyzed": len(chunks)}
        )
        db.add(audit)
        db.commit()
        
        yield f"data: {json.dumps({'status': 'complete'})}\n\n"

    return StreamingResponse(stream_analysis(), media_type="text/event-stream")

@router.get("/{doc_id}/report")
def get_report(
    doc_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    analysis = db.query(Analysis).filter(Analysis.document_id == doc_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"summary": analysis.summary_json, "risk": analysis.risk_json}

from pydantic import BaseModel
class RuleCreate(BaseModel):
    text: str

@router.get("/compliance-rules")
def get_rules(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    return db.query(ComplianceRule).filter(ComplianceRule.org_id == current_user.org_id).all()

@router.post("/compliance-rules")
def create_rule(
    rule_in: RuleCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_admin)
):
    rule = ComplianceRule(org_id=current_user.org_id, text=rule_in.text)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
