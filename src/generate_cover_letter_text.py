import sqlite3
import logging

from prompts import PROMPTS
from candidate_cv import BASE_CV
from claude_client import call_claude, setup_claude
from paths import DB_PATH

logger = logging.getLogger(__name__)

client, CONFIG, SCREENING = setup_claude("generate_cover_letter_text")


def run_cover_letter_generation():
    conn = sqlite3.connect(DB_PATH)

    placeholders = ", ".join("?" for _ in SCREENING["accepted_german_levels"])
    db_rows = conn.execute(
        f"""
        SELECT idFS, task, profile, usefulInfo FROM postings
        WHERE germanLevel IN ({placeholders}) AND affinityScore >= ? AND CL_Claude IS NULL
        """,
        SCREENING["accepted_german_levels"] + [SCREENING["min_affinity_score"]],
    ).fetchall()

    if len(db_rows) > CONFIG["max_cover_letters_per_run"]:
        logger.warning("max_cover_letters_per_run limit exceeded")
        db_rows = db_rows[:CONFIG["max_cover_letters_per_run"]]

    for id_fs, task, profile, useful_info in db_rows:
        job_text = f"Task: {task}\nProfile: {profile}\nUseful info: {useful_info}"

        prompt = (
            PROMPTS["cover_letter"]
            + f"\nJob posting:\n{job_text}\n"
            + f"\nCandidate's CV:\n{BASE_CV}\n"
        )

        cover_letter_body = call_claude(client, prompt, max_tokens=CONFIG["max_tokens"], model=CONFIG["model"])

        if len(cover_letter_body) > 2400:
            logger.warning("Max characters exceeded. Cover letter not saved")
            continue
        
        conn.execute("UPDATE postings SET CL_Claude = ? WHERE idFS = ?", (cover_letter_body, id_fs))
        conn.commit()

    conn.close()


if __name__ == "__main__":
    run_cover_letter_generation()
