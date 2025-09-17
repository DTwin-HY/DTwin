import os, json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()
SELECTED_MODEL = "gpt-5-nano"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model=SELECTED_MODEL, api_key=OPENAI_API_KEY)

import json

def call_llm(prompt: str, expect_json: bool = False, retries: int = 3):
    for i in range(retries):
        resp = llm.invoke([HumanMessage(content=prompt)])
        content = resp.content.strip()
        if expect_json:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                prompt += "\n\nPrevious response was not valid JSON. Respond ONLY in valid JSON."
        else:
            return content
    raise ValueError("LLM did not return valid JSON after retries")