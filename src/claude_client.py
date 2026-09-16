import json
import os
import anthropic
import logging

from paths import CONFIG_PATH
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

def setup_claude(stage_name):
    with open(CONFIG_PATH) as f:
        full_config = json.load(f)
    config = full_config[stage_name]
    screening = full_config["screening"]
    client = anthropic.Anthropic(api_key=os.environ[config["api_key_env_var"]])
    return client, config, screening


def call_claude(client, prompt, max_tokens, model):
    full_response = ""

    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "disabled"},
    ) as stream:
        for text in stream.text_stream:
            if logger.isEnabledFor(logging.DEBUG):
                print(text, end="", flush=True)
            full_response += text
        final_message = stream.get_final_message()

    logger.info(f"input_tokens: {final_message.usage.input_tokens}")
    logger.info(f"output_tokens: {final_message.usage.output_tokens}")

    return full_response.strip()
