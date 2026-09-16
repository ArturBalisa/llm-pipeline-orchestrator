import sqlite3
import logging

from prompts import PROMPTS
from gemini_client import call_gemini_with_retry, setup_gemini
from paths import DB_PATH

logger = logging.getLogger(__name__)

client, CONFIG, _ = setup_gemini("classify_german_level")

VALID_CEFR_VALUES = {"A1", "A2", "B1", "B2", "C1", "C2", "none"}


def run_classification():
    conn = sqlite3.connect(DB_PATH)

    db_rows = conn.execute("SELECT idFS, profile FROM postings WHERE germanLevel IS NULL").fetchall()
    
    for id_fs, job_text in db_rows:
        prompt = PROMPTS["german_level"] + job_text
        answer = call_gemini_with_retry(client, prompt, config=CONFIG)

        if answer not in VALID_CEFR_VALUES:
            logger.warning(f"unexpected response for {id_fs}: {answer!r}")
            continue

        logger.info(f"{id_fs}: {answer}")
        conn.execute("UPDATE postings SET germanLevel = ? WHERE idFS = ?", (answer, id_fs))
        conn.commit()

    conn.close()


if __name__ == "__main__":
    run_classification()
