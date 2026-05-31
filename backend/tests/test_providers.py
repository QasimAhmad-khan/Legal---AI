import pytest
from app.services.llm_provider import get_llm_provider
from app.services.embedding_provider import get_embedding_provider

def test_mock_llm_provider():
    llm = get_llm_provider("mock")
    result = llm.analyze_clause("test clause", ["precedent1"], ["rule1"])
    assert result.summary == "Mock summary"
    assert result.risk_score == "Low"
    assert result.compliance_verdict == "Pass"

def test_mock_embedding_provider():
    embedder = get_embedding_provider("mock")
    embedding = embedder.get_embedding("test text")
    assert len(embedding) == 1536
    assert embedding[0] == 0.0

def test_unknown_llm_provider():
    with pytest.raises(ValueError):
        get_llm_provider("invalid")

def test_unknown_embedding_provider():
    with pytest.raises(ValueError):
        get_embedding_provider("invalid")
