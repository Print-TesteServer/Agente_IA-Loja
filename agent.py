from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from config import GOOGLE_API_KEY, MODEL, TEMPERATURE
from prompts import SYSTEM_PROMPT
from tools import escalate_to_human


def build_agent():
    llm = ChatGoogleGenerativeAI(
        model=MODEL,
        temperature=TEMPERATURE,
        google_api_key=GOOGLE_API_KEY,
    )

    tools = [escalate_to_human]

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent
