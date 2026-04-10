from langchain_openai import ChatOpenAI
from services.AIAnalysis.utils.config import settings
import os

def get_mistral_llm(temperature: float = 0.3):
    """Initialize and return LLM instance via OpenRouter"""
    api_key = os.getenv("OPENROUTER_API_KEY", settings.MISTRAL_API_KEY)
    return ChatOpenAI(
        model="meta-llama/llama-3.3-70b-instruct:free",
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=temperature
    )
