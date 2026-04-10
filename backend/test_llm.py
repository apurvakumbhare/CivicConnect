import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("MISTRAL_API_KEY")

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

async def test_llm():
    llm = ChatOpenAI(
        model="mistralai/mistral-medium",
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.1,
    )
    try:
        res = await llm.ainvoke([HumanMessage(content="Hello")])
        print("Success:", res.content)
    except Exception as e:
        print("Error:", e)

    llm2 = ChatOpenAI(
        model="meta-llama/llama-3.1-8b-instruct:free",
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.1,
    )
    try:
        res = await llm2.ainvoke([HumanMessage(content="Hello")])
        print("Llama Success:", res.content)
    except Exception as e:
        print("Llama Error:", e)

asyncio.run(test_llm())
