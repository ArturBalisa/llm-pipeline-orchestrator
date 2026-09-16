import requests
import json
import time
import sqlite3
import re
import unicodedata
import random
import logging

from datetime import datetime
from zoneinfo import ZoneInfo
from paths import CONFIG_PATH, COMPANY_CONFIG_PATH, DB_PATH

logger = logging.getLogger(__name__)

with open(CONFIG_PATH) as f:
    SCREENING = json.load(f)["screening"]

with open(COMPANY_CONFIG_PATH) as f:
    COMPANY = json.load(f)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": COMPANY["referer"],
    "Accept": "*/*",
}

def contains_german_characters(text):
    german_chars = "äöüßÄÖÜ"
    for char in german_chars:
        if char in text:
            return True
    return False

def requires_advanced_degree(title):
    for keyword in SCREENING["excluded_title_keywords"]:
        if keyword.lower() in title.lower():
            return True
    return False

def build_listing_url(job_data):
    slug = f"{job_data['title']} {job_data['city']}"
    slug = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore").decode()
    slug = slug.replace("/", "_")
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return f"{COMPANY['job_base_url']}/{slug}?id={job_data['idClient']}"


def fetch_job_sections(id_fs):
    details = requests.get(
        COMPANY["ats_posting_url"].format(id=id_fs),
        headers=HEADERS
    ).json()
    sections = details.get("jobAd", {}).get("sections", {})
    return {
        "task": sections.get("jobDescription", {}).get("text", ""),
        "profile": sections.get("qualifications", {}).get("text", ""),
        "usefulInfo": sections.get("additionalInformation", {}).get("text", ""),
    }


def run_fetch():
    conn = sqlite3.connect(DB_PATH)

    params = {"indexName": COMPANY["search_index_name"], "page": 0, "q": "", "filter": json.dumps(COMPANY["job_filter"])}
    r = requests.get(COMPANY["listing_url"], params=params, headers=HEADERS)
    listings = r.json()["jobs"]

    logger.info(f"Fetched {len(listings)} postings")

    inserted_postings = 0
    skipped_idFS_duplicate = 0
    skipped_advanced_degree = 0
    skipped_german_duplicate = 0

    for v in listings:
        job_data = v["data"]

        existing_idFS = conn.execute(
            "SELECT 1 FROM postings WHERE idFS = ? UNION SELECT 1 FROM excluded_postings WHERE idFS = ?", (job_data["idFS"], job_data["idFS"],)
        ).fetchone()

        if existing_idFS:
            skipped_idFS_duplicate += 1
            continue

        if requires_advanced_degree(job_data["title"]):
            logger.info(f"Skipped (advanced degree): {job_data['title']}")
            skipped_advanced_degree += 1

            conn.execute(
            "INSERT OR IGNORE INTO excluded_postings (idFS, jobId, title, reason) VALUES (?, ?, ?, ?)",
            (job_data["idFS"], job_data["jobNumber"], job_data["title"], "Requires Advanced Degree"),
            )
            continue

        existing_job_id = conn.execute(
            "SELECT 1 FROM postings WHERE jobId = ?", (job_data["jobNumber"],)
        ).fetchone()

        sections = fetch_job_sections(job_data["idFS"])

        if existing_job_id:
            if contains_german_characters(job_data["title"] + sections["task"] + sections["profile"] + sections["usefulInfo"]):
                logger.info(f"Skipped (German duplicate): {job_data['title']}")
                skipped_german_duplicate += 1

                conn.execute(
                "INSERT OR IGNORE INTO excluded_postings (idFS, jobId, title, reason) VALUES (?, ?, ?, ?)",
                (job_data["idFS"], job_data["jobNumber"], job_data["title"], "Duplicate Contains German Characters"),
                )

                continue
            else:
                conn.execute("DELETE FROM postings WHERE jobId = ?", (job_data["jobNumber"],))

        job_field = ", ".join(job_data["jobField"])
        posting_url = build_listing_url(job_data)

        conn.execute("""
            INSERT OR IGNORE INTO postings (idFS, jobId, title, jobField, url, postingDate, collectionDate, task, profile, usefulInfo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_data["idFS"],
            job_data["jobNumber"],
            job_data["title"],
            job_field,
            posting_url,
            job_data["postingDate"],
            datetime.now(ZoneInfo("Europe/Berlin")).isoformat(),
            sections["task"],
            sections["profile"],
            sections["usefulInfo"],
        ))

        inserted_postings += 1

        time.sleep(random.uniform(1, 3))

    conn.commit()
    conn.close()

    logger.info(
        f"Fetch finished: {inserted_postings} inserted, "
        f"{skipped_idFS_duplicate} skipped (idFS duplicate), "
        f"{skipped_advanced_degree} skipped (advanced degree), "
        f"{skipped_german_duplicate} skipped (German duplicate)"
    )


if __name__ == "__main__":
    run_fetch()
