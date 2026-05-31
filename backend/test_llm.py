import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.chunk import Chunk
from app.services.llm_provider import get_llm_provider
from app.core.config import settings
from app.api.endpoints.precedents import retrieve_similar_precedents
import dotenv

dotenv.load_dotenv()

engine = create_engine("postgresql://admin:password@localhost:5432/legal_analyzer")
Session = sessionmaker(bind=engine)
db = Session()

chunk = db.query(Chunk).first()
print("Chunk length:", len(chunk.text))

llm = get_llm_provider(settings.LLM_PROVIDER, settings.LLM_API_KEY)
print(f"Using Provider: {settings.LLM_PROVIDER}")

precedents = retrieve_similar_precedents(db, chunk.embedding, top_k=2)
print("Precedents:", precedents)

try:
    res = llm.analyze_clause(chunk.text, precedents, [])
    print("Result:", res)
except Exception as e:
    print("Error:", e)
