import os
import pandas as pd
from pydantic import BaseModel, Field, ValidationError

# ==========================================================
# File Paths
# ==========================================================

RAW_FILE = "data/raw/scraped.csv"

VALID_FILE = "data/raw/scraped_valid.csv"

DEAD_FILE = "data/logs/dead_letter.csv"

REPORT_FILE = "data/logs/validation_report.txt"

os.makedirs("data/logs", exist_ok=True)

# ==========================================================
# Pydantic Schema
# ==========================================================

class ScrapedRecord(BaseModel):

    type: str = Field(..., min_length=2)

    content: str = Field(..., min_length=1)

    url: str | None = None


# ==========================================================
# Completeness Score
# ==========================================================

def completeness_score(record):

    total = len(record)

    filled = sum(
        1
        for value in record.values()
        if pd.notna(value) and str(value).strip() != ""
    )

    return round((filled / total) * 100, 2)


# ==========================================================
# Check File
# ==========================================================

if not os.path.exists(RAW_FILE):

    print("scraped.csv not found.")

    exit()


# ==========================================================
# Read CSV
# ==========================================================

df = pd.read_csv(RAW_FILE)

print(f"\nLoaded {len(df)} records")

valid_records = []

dead_records = []

# ==========================================================
# Validation Loop
# ==========================================================

for _, row in df.iterrows():

    record = row.to_dict()

    # Replace NaN with empty string
    for key in record:

        if pd.isna(record[key]):
            record[key] = ""

    score = completeness_score(record)

    try:

        item = ScrapedRecord(

            type=str(record["type"]).strip(),

            content=str(record["content"]).strip(),

            url=str(record["url"]).strip()

        )

        output = item.model_dump()

        output["completeness_score"] = score

        valid_records.append(output)

    except ValidationError as e:

        record["reason"] = str(e)

        record["completeness_score"] = score

        dead_records.append(record)

# ==========================================================
# Save Files
# ==========================================================

valid_df = pd.DataFrame(valid_records)

dead_df = pd.DataFrame(dead_records)

valid_df.to_csv(VALID_FILE, index=False)

dead_df.to_csv(DEAD_FILE, index=False)

# ==========================================================
# Validation Report
# ==========================================================

total = len(df)

valid = len(valid_df)

rejected = len(dead_df)

acceptance = round((valid / total) * 100, 2) if total else 0

with open(REPORT_FILE, "w") as report:

    report.write("=====================================\n")
    report.write(" SCRAPED DATA VALIDATION REPORT\n")
    report.write("=====================================\n\n")

    report.write(f"Total Records      : {total}\n")
    report.write(f"Valid Records      : {valid}\n")
    report.write(f"Rejected Records   : {rejected}\n")
    report.write(f"Acceptance Rate    : {acceptance}%\n")

# ==========================================================
# Console Output
# ==========================================================

print("\n=====================================")
print("Validation Completed Successfully")
print("=====================================")
print(f"Total Records      : {total}")
print(f"Valid Records      : {valid}")
print(f"Rejected Records   : {rejected}")
print(f"Acceptance Rate    : {acceptance}%")
print(f"Accepted File      : {VALID_FILE}")
print(f"Dead Letter Queue  : {DEAD_FILE}")
print(f"Validation Report  : {REPORT_FILE}")
print("=====================================")