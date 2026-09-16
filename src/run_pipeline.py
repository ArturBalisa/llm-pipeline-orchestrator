import logging

from init_database import init_database
from fetch_listings import run_fetch
from classify_german_level import run_classification
from extract_keywords import run_keyword_extraction
from calculate_affinity_score import run_affinity_scoring
from generate_cover_letter_text import run_cover_letter_generation
from build_cover_letter_pdf import generate_cover_letter
from paths import LOGS_DIR

logger = logging.getLogger("run_pipeline")

def setup_logging():
    LOGS_DIR.mkdir(exist_ok=True)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    file_handler = logging.FileHandler(LOGS_DIR / "pipeline.log")
    file_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s [%(name)s]: %(message)s",
        handlers=[console_handler, file_handler],
    )




def run_stage(name, func):
    logger.info(f"     ---------- starting {name} ----------\n")
    try:
        func()
    except Exception:
        logger.exception(f"{name} failed")


if __name__ == "__main__":
    setup_logging()
    
    run_stage("init_database", init_database)
    run_stage("run_fetch", run_fetch)
    run_stage("run_classification", run_classification)
    run_stage("run_affinity_scoring", run_affinity_scoring)
    run_stage("run_keyword_extraction", run_keyword_extraction)
    run_stage("run_cover_letter_generation", run_cover_letter_generation)
    run_stage("generate_cover_letter", generate_cover_letter)
