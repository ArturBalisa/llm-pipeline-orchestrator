import json
import os
import re
import time
import logging

from google import genai
from google.genai import types, errors
from paths import CONFIG_PATH
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MAX_RETRIES = 5
RETRY_WAIT_503_SECONDS = 3
RETRY_WAIT_429_SECONDS = 60


def setup_gemini(stage_name):
    with open(CONFIG_PATH) as f:
        full_config = json.load(f)
    config = full_config[stage_name]
    screening = full_config["screening"]
    client = genai.Client(api_key=os.environ[config["api_key_env_var"]])
    return client, config, screening


def call_gemini(client, prompt, max_tokens, model):
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=0,
        ),
    )

    logger.debug(f"finish_reason: {response.candidates[0].finish_reason}")
    logger.debug(f"usage: {response.usage_metadata}")

    return response.text.strip()


def _parse_retry_delay(exc, default):
    match = re.search(r"retryDelay': '([\d.]+)s'", str(exc))
    if match:
        return float(match.group(1))
    else:
        return default


def call_gemini_with_retry(client, prompt, config):
    models = [config["primary_model"], config["fallback_model"]]
    for model in models:
        logger.info(f"Using model: {model}")
        for attempt in range(MAX_RETRIES):
            try:
                return call_gemini(client, prompt, config["max_tokens"], model)
            except errors.APIError as exc:
                if exc.code not in (503, 429):
                    logger.error(f"Unexpected error {exc.code}: {exc}")
                    return None

                if exc.code == 503:
                    logger.info(f"Error 503. Wait for {RETRY_WAIT_503_SECONDS} seconds")
                    time.sleep(RETRY_WAIT_503_SECONDS)
                    continue

                if "PerDay" in str(exc):
                    logger.warning(f"Error 429: {exc}. Daily quota exceeded for this model.")
                    break

                wait_seconds = _parse_retry_delay(exc, RETRY_WAIT_429_SECONDS)
                logger.info(f"Error 429: {exc}. Wait for {wait_seconds} seconds")
                time.sleep(wait_seconds)

    return None
