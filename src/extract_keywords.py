import sqlite3
import logging

from prompts import PROMPTS
from gemini_client import call_gemini_with_retry, setup_gemini
from paths import DB_PATH

logger = logging.getLogger(__name__)

client, CONFIG, SCREENING = setup_gemini("extract_keywords")


def run_keyword_extraction():
    conn = sqlite3.connect(DB_PATH)

    if SCREENING["skip_keywords_gate"]:
        db_rows = conn.execute(
            "SELECT idFS, task, profile FROM postings WHERE positionKeyWords IS NULL"
        ).fetchall()
    else:
        db_rows = conn.execute(
            "SELECT idFS, task, profile FROM postings WHERE positionKeyWords IS NULL AND affinityScore >= ?",
            (SCREENING["min_affinity_score"],),
        ).fetchall()

    for id_fs, task, profile in db_rows:
        job_text = f"Task: {task}\nProfile: {profile}"
        prompt = PROMPTS["keywords"] + job_text

        answer = call_gemini_with_retry(client, prompt, config=CONFIG)

        if answer is None:
            continue

        logger.info(f"{id_fs}: {answer}")

        conn.execute(
            "UPDATE postings SET positionKeyWords = ? WHERE idFS = ?",
            (answer, id_fs),
        )
        conn.commit()

    conn.close()


if __name__ == "__main__":
    run_keyword_extraction()
