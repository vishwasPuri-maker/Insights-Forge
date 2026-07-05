import os
import time
import logging
import subprocess
import sys

# ==========================================================
# FOLDERS
# ==========================================================

LOG_FOLDER = "data/logs"
SCRAPED_FILE = "data/raw/scraped.csv"

os.makedirs(LOG_FOLDER, exist_ok=True)

# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================

logging.basicConfig(
    filename=os.path.join(LOG_FOLDER, "pipeline.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ==========================================================
# FUNCTION TO RUN EACH STEP
# ==========================================================

def run_step(step_name, command):

    print(f"\n========== {step_name} ==========")
    logging.info(f"{step_name} Started")

    start = time.time()

    try:

        subprocess.run(
            command,
            shell=True,
            check=True
        )

        end = time.time()

        duration = round(end - start, 2)

        print(f"{step_name} Completed ({duration} sec)")
        logging.info(f"{step_name} Completed ({duration} sec)")

    except subprocess.CalledProcessError as e:

        print(f"{step_name} Failed")

        logging.error(f"{step_name} Failed")
        logging.error(str(e))

        sys.exit(1)


# ==========================================================
# MAIN PIPELINE
# ==========================================================

def main():

    print("\n===================================================")
    print("      GOVERNMENT ETL PIPELINE STARTED")
    print("===================================================")

    logging.info("Pipeline Started")

    # ------------------------------------------------------
    # STEP 1 : WEB SCRAPING
    # ------------------------------------------------------

    print("\n========== Web Scraping ==========")

    if os.path.exists(SCRAPED_FILE):

        print("scraped.csv already exists.")
        print("Skipping Web Scraping.")

        logging.info("Web Scraping Skipped")

    else:

        run_step(
            "Web Scraping",
            f'"{sys.executable}" scraper/scraper.py'
        )

    # ------------------------------------------------------
    # STEP 2 : DATA VALIDATION
    # ------------------------------------------------------

    run_step(
        "Data Validation",
        f'"{sys.executable}" scraper/validation.py'
    )

    # ------------------------------------------------------
    # STEP 3 : EXTRACT
    # ------------------------------------------------------

    run_step(
        "Extract",
        f'"{sys.executable}" etl/extract.py'
    )

    # ------------------------------------------------------
    # STEP 4 : TRANSFORM
    # ------------------------------------------------------

    run_step(
        "Transform",
        f'"{sys.executable}" etl/transform.py'
    )

    # ------------------------------------------------------
    # STEP 5 : LOAD
    # ------------------------------------------------------

    run_step(
        "Load",
        f'"{sys.executable}" etl/load.py'
    )

    logging.info("Pipeline Finished Successfully")

    print("\n===================================================")
    print("      PIPELINE EXECUTED SUCCESSFULLY")
    print("===================================================")


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()