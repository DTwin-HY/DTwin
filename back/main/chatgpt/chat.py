import os
from dotenv import load_dotenv
import requests

from loguru import logger


load_dotenv()
API_URL = "https://api.openai.com/v1/responses"
SELECTED_MODEL = "gpt-5-nano"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TIMEOUT = 10  # seconds


def send_prompt(prompt: str) -> requests.Response:
    response = requests.post(
        url=API_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        json={"model": SELECTED_MODEL, "input": prompt},
        timeout=TIMEOUT,
    )

    return response


def answer(prompt: str) -> dict[str, str]:

    response = send_prompt(prompt)

    if response.text == "":
        logger.error("Got empty response")

    response_json = response.json()

    response_text = ""

    try:
        for output_idx in response_json["output"]:
            if "content" in output_idx:
                response_text = output_idx["content"][0]["text"]
    except KeyError:
        logger.error("Invalid response")

    return {"message": response_text}
