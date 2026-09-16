import sqlite3
import logging

from prompts import PROMPTS
from candidate_cv import CV_SKILLS
from gemini_client import call_gemini_with_retry, setup_gemini
from paths import DB_PATH

logger = logging.getLogger(__name__)

client, CONFIG, SCREENING = setup_gemini("calculate_affinity_score")

VALID_AFFINITY_SCORES = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}


def run_affinity_scoring():
    conn = sqlite3.connect(DB_PATH)

    if SCREENING["skip_affinity_gate"]:
        db_rows = conn.execute(
            "SELECT idFS, task, profile FROM postings WHERE affinityScore IS NULL"
        ).fetchall()
    else:
        placeholders = ", ".join("?" for _ in SCREENING["accepted_german_levels"])
        db_rows = conn.execute(
            f"""
            SELECT idFS, task, profile FROM postings
            WHERE affinityScore IS NULL AND germanLevel IN ({placeholders})
            """,
            SCREENING["accepted_german_levels"],
        ).fetchall()

    for id_fs, task, profile in db_rows:
        candidate_skills = f"Candidate's skills:\n{CV_SKILLS}\n\n"
        job_text = f"Job posting:\nTask: {task}\nProfile: {profile}"
        prompt = PROMPTS["affinity_score"] + candidate_skills + job_text

        answer = call_gemini_with_retry(client, prompt, config=CONFIG)

        if answer not in VALID_AFFINITY_SCORES:
            logger.warning(f"unexpected response for {id_fs}: {answer!r}")
            continue

        logger.info(f"{id_fs}: {answer}")
        conn.execute("UPDATE postings SET affinityScore = ? WHERE idFS = ?", (int(answer), id_fs))
        conn.commit()

    conn.close()


if __name__ == "__main__":
    run_affinity_scoring()
