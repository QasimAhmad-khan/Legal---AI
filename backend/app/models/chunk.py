from sqlalchemy import Column, Integer, String, ForeignKey, Text
from pgvector.sqlalchemy import Vector
from app.db.session import Base

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    text = Column(Text, nullable=False)
    char_start = Column(Integer)
    char_end = Column(Integer)
    clause_type = Column(String)
    embedding = Column(Vector(1536)) # Assuming OpenAI 1536 dims for now
    
class Precedent(Base):
    __tablename__ = "precedents"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), index=True)
    filename = Column(String, nullable=False)
    # add created_at if needed, keeping simple

class PrecedentChunk(Base):
    __tablename__ = "precedent_chunks"

    id = Column(Integer, primary_key=True, index=True)
    precedent_id = Column(Integer, ForeignKey("precedents.id"), index=True)
    text = Column(Text, nullable=False)
    clause_type = Column(String)
    embedding = Column(Vector(1536))
