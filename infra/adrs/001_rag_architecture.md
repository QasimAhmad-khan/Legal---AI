# ADR 001: RAG Architecture using pgvector

## Status
Accepted

## Context
Law firms need to ensure that AI-generated contract summaries and risk flags are grounded in their own internal precedent documents, rather than generic data from a foundational LLM. We need a fast, reliable, and easily deployable way to store embeddings of these precedents and perform similarity searches.

## Decision
We will use **PostgreSQL with the `pgvector` extension** to store precedent chunks and their embeddings. We will use cosine similarity to retrieve the top-K most relevant chunks during the prompt chain for contract analysis.

## Rationale
1. **Consolidation**: Since we are already using PostgreSQL for our application database (Users, Documents, Analyses), adding `pgvector` allows us to avoid introducing an additional infrastructure dependency (like Pinecone or Weaviate).
2. **Metadata Filtering**: RDBMS allows us to easily filter vectors by metadata (e.g., `clause_type`, `org_id`) using standard SQL `WHERE` clauses alongside the vector distance operators.
3. **Cost and Simplicity**: `pgvector` is open-source and natively supported by many managed PostgreSQL providers (like AWS RDS, Supabase, Neon).

## Consequences
- **Positive**: Simplified infrastructure, transactional consistency between business logic and embeddings, zero extra cost.
- **Negative**: `pgvector` scales well for millions of vectors using HNSW indexes, but may become less performant than dedicated vector DBs at the scale of billions of vectors. For the scope of a firm's precedent library, this limit is highly unlikely to be reached.
