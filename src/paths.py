from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"
COMPANY_CONFIG_PATH = PROJECT_ROOT / "company.json"
DB_PATH = PROJECT_ROOT / "data" / "postings.db"
TEMPLATE_PATH = PROJECT_ROOT / "templates" / "template.tex"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"
