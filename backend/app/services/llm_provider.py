from abc import ABC, abstractmethod
import json
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class AnalysisResult(BaseModel):
    summary: str
    risk_score: str
    compliance_verdict: str

class LLMProvider(ABC):
    @abstractmethod
    def _call_model(self, prompt: str) -> str:
        pass

    def analyze_clause(self, clause_text: str, precedents: List[str], compliance_rules: List[str], max_retries: int = 3) -> AnalysisResult:
        prompt = f"""
        Analyze the following contract clause.
        
        Clause:
        {clause_text}
        
        Firm Precedents:
        {precedents}
        
        Compliance Rules:
        {compliance_rules}
        
        Provide a plain-English summary (max 3 sentences), a risk_score (Low/Medium/High), and a compliance_verdict (Pass/Fail with rationale).
        Output MUST be valid JSON matching this schema:
        {{
            "summary": "string",
            "risk_score": "string",
            "compliance_verdict": "string"
        }}
        """
        
        for attempt in range(max_retries):
            try:
                response_text = self._call_model(prompt)
                
                # Clean up potential markdown formatting
                if response_text.startswith("```json"):
                    response_text = response_text[7:-3]
                elif response_text.startswith("```"):
                    response_text = response_text[3:-3]
                    
                data = json.loads(response_text)
                result = AnalysisResult(**data)
                return result
            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    return AnalysisResult(
                        summary=f"Analysis failed after {max_retries} attempts. Error: {str(e)}",
                        risk_score="High",
                        compliance_verdict="Fail: Analysis Error"
                    )
        
        return AnalysisResult(summary="Failed", risk_score="High", compliance_verdict="Fail")

class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str):
        import openai
        self.client = openai.Client(api_key=api_key)

    def _call_model(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a legal AI assistant. Output JSON with summary, risk_score, and compliance_verdict."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content

class AnthropicLLMProvider(LLMProvider):
    def __init__(self, api_key: str):
        # Requires anthropic package
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)

    def _call_model(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system="You are a legal AI assistant. Output JSON with summary, risk_score, and compliance_verdict.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_key: str):
        from google import genai
        self.client = genai.Client(api_key=api_key)

    def _call_model(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents="You are a legal AI assistant. Output JSON with summary, risk_score, and compliance_verdict.\n" + prompt
        )
        return response.text

class MockLLMProvider(LLMProvider):
    def _call_model(self, prompt: str) -> str:
        return '{"summary": "Mock summary", "risk_score": "Low", "compliance_verdict": "Pass"}'

def get_llm_provider(provider_name: str, api_key: Optional[str] = None) -> LLMProvider:
    provider_name = provider_name.lower()
    if provider_name == "openai":
        return OpenAILLMProvider(api_key)
    elif provider_name == "anthropic":
        return AnthropicLLMProvider(api_key)
    elif provider_name == "gemini":
        return GeminiLLMProvider(api_key)
    elif provider_name == "mock":
        return MockLLMProvider()
    raise ValueError(f"Unknown LLM provider: {provider_name}")
