import sqlite3
import logging

from paths import DB_PATH

logger = logging.getLogger(__name__)


def init_database():
    conn = sqlite3.connect(DB_PATH)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS postings (
            idFS TEXT PRIMARY KEY,
            jobId TEXT,
            title TEXT,
            jobField TEXT,
            url TEXT,
            postingDate TEXT,
            collectionDate TEXT,
            task TEXT,
            profile TEXT,
            usefulInfo TEXT,
            germanLevel TEXT,
            affinityScore INTEGER,
            positionKeyWords TEXT,
            CL_Claude TEXT)
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS excluded_postings (
            idFS TEXT PRIMARY KEY,
            jobId TEXT,
            title TEXT,
            reason TEXT)
    """)

#    Under development
#    conn.execute("""
#        CREATE TABLE IF NOT EXISTS overview (
#            run INTEGER PRIMARY KEY AUTOINCREMENT,
#            date TEXT,
#            inserted_posts INT,
#            skipped_idFS INT,
#            skipped_degree INT,
#            skipped_german INT,
#            high_german_level_required INT,
#            low_affinity_score INT,
#            extracted_key_words INT,
#            generated_cover_letters INT)
#    """)

    
    conn.commit()
    conn.close()
    logger.info(f"Database ready: {DB_PATH}")


if __name__ == "__main__":
    init_database()
