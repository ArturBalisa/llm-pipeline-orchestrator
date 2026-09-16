import sqlite3
import subprocess
import os
import shutil
import re
import json
import logging

from paths import DB_PATH, TEMPLATE_PATH, OUTPUT_DIR, COMPANY_CONFIG_PATH

logger = logging.getLogger(__name__)

with open(COMPANY_CONFIG_PATH) as f:
    COMPANY = json.load(f)

LATEX_SPECIAL_CHARS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

MONTH_NAMES = {
    1: "01. January", 2: "02. February", 3: "03. March", 4: "04. April",
    5: "05. May", 6: "06. June", 7: "07. July", 8: "08. August",
    9: "09. September", 10: "10. October", 11: "11. November", 12: "12. December",
}


def escape_latex(text):
    pattern = re.compile("|".join(re.escape(char) for char in LATEX_SPECIAL_CHARS))
    return pattern.sub(lambda match: LATEX_SPECIAL_CHARS[match.group()], text)


def write_job_info_txt(output_dir, job_id, id_fs, job_title, job_field, posting_date, german_level, job_url):
    info_path = f"{output_dir}/{job_id}.txt"

    if os.path.exists(info_path):
        return
    
    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"Title: {job_title}\n\n")
        f.write(f"Job ID: {job_id}\n\n")
        f.write(f"idFS: {id_fs}\n\n")
        f.write(f"Job Field: {job_field}\n\n")
        f.write(f"Posting Date: {posting_date}\n\n")
        f.write(f"German Level: {german_level}\n\n")
        f.write(f"URL: {job_url}\n")


def write_cover_letter_pdf(output_dir, job_id, template_text, job_title, cover_letter_body):
    pdf_path = f"{output_dir}/{job_id}.pdf"

    if os.path.exists(pdf_path):
        return
    
    replacements = {
        "<<COMPANY_NAME>>": COMPANY["company_name"],
        "<<COMPANY_ADDRESS>>": COMPANY["company_address"],
        "<<COMPANY_ZIP>>": COMPANY["company_zip"],
        "<<COMPANY_CITY>>": COMPANY["company_city"],
        "<<COMPANY_COUNTRY>>": COMPANY["company_country"],
        "<<JOB_TITLE>>": escape_latex(job_title),
        "<<COVER_LETTER_BODY>>": escape_latex(cover_letter_body),
    }

    filled_text = template_text
    for marker, value in replacements.items():
        filled_text = filled_text.replace(marker, value)

    output_path = f"{output_dir}/{job_id}.tex"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(filled_text)

    logger.info(f"Saved {output_path}")

    compile_pdf(output_path)


def generate_cover_letter():
    conn = sqlite3.connect(DB_PATH)
    db_rows = conn.execute(
        "SELECT jobId, idFS, title, jobField, CL_Claude, postingDate, germanLevel, url FROM postings WHERE CL_Claude IS NOT NULL"
    ).fetchall()
    conn.close()

    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        template_text = f.read()

    for job_id, id_fs, job_title, job_field, cover_letter_body, posting_date, german_level, job_url in db_rows:
        month_number = int(posting_date[5:7])
        day_folder = posting_date[8:10]
        output_dir = OUTPUT_DIR / MONTH_NAMES[month_number] / day_folder
        os.makedirs(output_dir, exist_ok=True)

        write_job_info_txt(output_dir, job_id, id_fs, job_title, job_field, posting_date, german_level, job_url)
        write_cover_letter_pdf(output_dir, job_id, template_text, job_title, cover_letter_body)


def compile_pdf(tex_path):
    pdflatex_path = shutil.which("pdflatex")
    if pdflatex_path is None:
        raise RuntimeError(
            "pdflatex not found. Make sure a LaTeX distribution is installed."
        )

    output_dir = os.path.dirname(tex_path)

    result = subprocess.run(
        [pdflatex_path, "-interaction=nonstopmode", f"-output-directory={output_dir}", tex_path],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error(result.stdout)
        logger.error(result.stderr)
        raise RuntimeError(f"pdflatex failed for {tex_path}")

    base_name = os.path.splitext(tex_path)[0]
    for ext in (".aux", ".log", ".out"):
        aux_file = base_name + ext
        if os.path.exists(aux_file):
            os.remove(aux_file)

    os.remove(tex_path)

    logger.info(f"Compiled {base_name}.pdf")


if __name__ == "__main__":
    generate_cover_letter()
