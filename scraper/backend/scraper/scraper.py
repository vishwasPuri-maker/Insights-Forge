import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

# ==========================================================
# Configuration
# ==========================================================

URL = "https://www.myscheme.gov.in"

OUTPUT_FOLDER = "data/raw"
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "scraped.csv")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}

# ==========================================================
# Download Website
# ==========================================================

print("Connecting to website...")

try:

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

except RequestException as e:

    print("\nUnable to fetch website.")
    print(f"Reason: {e}")

    # Don't overwrite an existing scraped.csv
    if os.path.exists(OUTPUT_FILE):
        print("\nExisting scraped.csv found.")
        print("Using existing file.")
        exit(0)

    print("No existing scraped.csv available.")
    exit(1)

# ==========================================================
# Parse HTML
# ==========================================================

print("Parsing HTML...")

soup = BeautifulSoup(response.text, "html.parser")

page_title = soup.title.get_text(strip=True) if soup.title else "Unknown"

print(f"Website Title : {page_title}")

# ==========================================================
# Collect Data
# ==========================================================

records = []

# H1
for tag in soup.find_all("h1"):

    text = tag.get_text(" ", strip=True)

    if text:

        records.append({
            "type": "Heading H1",
            "content": text,
            "url": ""
        })

# H2
for tag in soup.find_all("h2"):

    text = tag.get_text(" ", strip=True)

    if text:

        records.append({
            "type": "Heading H2",
            "content": text,
            "url": ""
        })

# H3
for tag in soup.find_all("h3"):

    text = tag.get_text(" ", strip=True)

    if text:

        records.append({
            "type": "Heading H3",
            "content": text,
            "url": ""
        })

# Links
for tag in soup.find_all("a"):

    text = tag.get_text(" ", strip=True)

    href = tag.get("href", "")

    if text or href:

        records.append({
            "type": "Link",
            "content": text,
            "url": href
        })

# ==========================================================
# Create DataFrame
# ==========================================================

df = pd.DataFrame(records)

df.drop_duplicates(inplace=True)

df.reset_index(drop=True, inplace=True)

# ==========================================================
# Save CSV
# ==========================================================

df.to_csv(OUTPUT_FILE, index=False)

# ==========================================================
# Summary
# ==========================================================

print("\n======================================")
print("SCRAPING COMPLETED")
print("======================================")
print(f"Website          : {URL}")
print(f"Page Title       : {page_title}")
print(f"Total Records    : {len(df)}")
print(f"Output File      : {OUTPUT_FILE}")
print("======================================")