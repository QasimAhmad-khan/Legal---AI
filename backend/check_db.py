from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.document import Document
from app.models.chunk import Chunk

engine = create_engine("postgresql://admin:password@localhost:5432/legal_analyzer")
Session = sessionmaker(bind=engine)
db = Session()

docs = db.query(Document).all()
for d in docs:
    chunks_count = db.query(Chunk).filter(Chunk.document_id == d.id).count()
    print(f"Doc {d.id}: {d.filename} | Status: {d.status} | Chunks: {chunks_count}")
