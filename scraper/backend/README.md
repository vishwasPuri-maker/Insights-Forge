````markdown
# Government Data Engineering ETL Pipeline

A complete end-to-end **Data Engineering ETL Pipeline** built using Python, Pandas, FastAPI, Pydantic, Requests, and BeautifulSoup.

This project automates the full lifecycle of data:
- Data collection
- Web scraping
- Validation
- Cleaning
- Transformation
- Loading
- API serving

It simulates a real-world production-grade data engineering system for government datasets.

---

# Project Overview

This system processes multiple government datasets and external scraped data using a modular ETL architecture.

It ensures:
- Data quality through validation
- Fault tolerance via dead letter queue
- Standardized transformations
- API-based data access
- Logging for observability

The project is designed for learning **Data Engineering, Backend Systems, and ETL Architecture**.

---

# Key Features

- Multi-source data ingestion (CSV + web scraping)
- Automated ETL pipeline
- Pydantic-based validation layer
- Completeness score calculation
- Dead Letter Queue for invalid records
- Data cleaning & standardization engine
- Structured logging system
- REST API using FastAPI
- Swagger UI documentation
- Modular pipeline architecture

---

# Repository Structure

```text
Government-Data-Engineering-ETL-Pipeline/
│
├── api.py
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── data/
│   ├── raw/
│   │   ├── education.csv
│   │   ├── employment.csv
│   │   ├── government_schemes.csv
│   │   ├── healthcare_dataset.csv
│   │   ├── india_agriculture_crop_production.csv
│   │   ├── scraped.csv
│   │   └── scraped_valid.csv
│   │
│   ├── cleaned/
│   │   ├── education_clean.csv
│   │   ├── employment_clean.csv
│   │   ├── government_schemes_clean.csv
│   │   ├── healthcare_dataset_clean.csv
│   │   ├── india_agriculture_crop_production_clean.csv
│   │   └── scraped_clean.csv
│   │
│   └── logs/
│       ├── pipeline.log
│       ├── validation_report.txt
│       └── dead_letter.csv
│
├── scraper/
│   ├── scraper.py
│   └── validation.py
│
└── etl/
    ├── extract.py
    ├── transform.py
    └── load.py
````

---

# ETL Pipeline Architecture

```text
Raw Data Sources + Web Scraping
            ↓
        Extract Layer
            ↓
      Validation Layer (Pydantic)
            ↓
   Dead Letter Queue (Invalid Data)
            ↓
        Transform Layer
            ↓
        Cleaning Engine
            ↓
        Load Layer
            ↓
        FastAPI Service
            ↓
        JSON Response
```

---

# ETL Pipeline Modules

## 1. Extract Module

Responsible for reading raw data from multiple sources.

### Responsibilities

* Load CSV datasets
* Read scraped data
* Inspect schema
* Basic data preview

### Code Example

```python
import pandas as pd

df = pd.read_csv("data/raw/government_schemes.csv")

print(df.head())
print(df.info())
```

---

## 2. Transform Module

Responsible for cleaning and standardizing datasets.

### Responsibilities

* Remove duplicates
* Handle missing values
* Standardize column names
* Normalize whitespace
* Convert inconsistent formats

### Code Example

```python
import os
import pandas as pd

RAW_FOLDER = "data/raw"
CLEAN_FOLDER = "data/cleaned"

os.makedirs(CLEAN_FOLDER, exist_ok=True)

for file in os.listdir(RAW_FOLDER):
    if file.endswith(".csv"):

        path = os.path.join(RAW_FOLDER, file)
        df = pd.read_csv(path)

        df = df.drop_duplicates()
        df = df.dropna(how="all")

        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip()

        df = df.fillna("Unknown")

        output_path = os.path.join(
            CLEAN_FOLDER,
            file.replace(".csv", "_clean.csv")
        )

        df.to_csv(output_path, index=False)
```

---

## 3. Load Module

Responsible for loading cleaned datasets for API consumption.

### Responsibilities

* Read cleaned files
* Load datasets into memory
* Validate availability

### Code Example

```python
import os
import pandas as pd

CLEAN_FOLDER = "data/cleaned"

datasets = {}

for file in os.listdir(CLEAN_FOLDER):
    if file.endswith(".csv"):
        path = os.path.join(CLEAN_FOLDER, file)
        datasets[file] = pd.read_csv(path)

print("Datasets Loaded")
print(list(datasets.keys()))
```

---

# FastAPI Application

## Features

* REST API endpoints
* JSON responses
* Swagger UI (/docs)
* OpenAPI schema
* File-based dataset serving

---

## Core Setup

```python
from fastapi import FastAPI, HTTPException
import pandas as pd
import os

app = FastAPI(title="Government ETL Pipeline API")

DATA_FOLDER = "data/cleaned"
```

---

## Dataset Loader Function

```python
def load_dataset(filename: str):

    file_path = os.path.join(DATA_FOLDER, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    df = pd.read_csv(file_path)
    df = df.where(pd.notnull(df), None)

    return {
        "dataset": filename,
        "total_records": len(df),
        "columns": list(df.columns),
        "data": df.to_dict(orient="records")
    }
```

---

## API Endpoints

```python
@app.get("/")
def home():
    return {
        "project": "Government ETL Pipeline",
        "status": "Running"
    }
```

```python
@app.get("/education")
def education():
    return load_dataset("education_clean.csv")
```

```python
@app.get("/employment")
def employment():
    return load_dataset("employment_clean.csv")
```

```python
@app.get("/government")
def government():
    return load_dataset("government_schemes_clean.csv")
```

```python
@app.get("/healthcare")
def healthcare():
    return load_dataset("healthcare_dataset_clean.csv")
```

```python
@app.get("/agriculture")
def agriculture():
    return load_dataset("india_agriculture_crop_production_clean.csv")
```

```python
@app.get("/scraped")
def scraped():
    return load_dataset("scraped_clean.csv")
```

---

## API Response Format

```json
{
  "dataset": "education_clean.csv",
  "total_records": 1200,
  "columns": ["scheme_name", "category", "state"],
  "data": [
    {
      "scheme_name": "Education Scheme A",
      "category": "Scholarship",
      "state": "India"
    }
  ]
}
```

---

# Data Validation System

## Pydantic Model

```python
from pydantic import BaseModel, Field

class Scheme(BaseModel):
    scheme_name: str = Field(..., min_length=3)
    category: str
    state: str
    description: str
```

---

## Completeness Score Logic

```python
def completeness_score(record):
    total = len(record)
    filled = sum(
        1 for v in record.values()
        if v is not None and str(v).strip() != ""
    )
    return round((filled / total) * 100, 2)
```

---

## Dead Letter Queue

Location:

```
data/logs/dead_letter.csv
```

Stores:

* Invalid records
* Validation errors
* Failed entries
* Completeness scores

---

## Validation Report

Location:

```
data/logs/validation_report.txt
```

Includes:

* Total records processed
* Valid records
* Rejected records
* Acceptance rate

---

# Data Flow

```text
Raw Data + Scraping
        ↓
Validation Layer
        ↓
Dead Letter Queue
        ↓
ETL Processing
        ↓
Cleaning Engine
        ↓
Clean Storage
        ↓
FastAPI Layer
        ↓
JSON API Response
```

---

# Output Structure

```text
data/
├── raw/
├── cleaned/
└── logs/
    ├── pipeline.log
    ├── validation_report.txt
    └── dead_letter.csv
```

---

# Future Improvements

* PostgreSQL integration
* Apache Airflow orchestration
* Docker containerization
* Kafka streaming pipeline
* AWS S3 storage
* CI/CD pipeline automation
* Real-time analytics dashboard
* Authentication system
* Monitoring & alerts system

---

# Requirements

```text
fastapi
uvicorn
pandas
numpy
requests
beautifulsoup4
pydantic
```

---

# How to Run

## Step 1: Install dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Run ETL pipeline

```bash
python main.py
```

## Step 3: Start API server

```bash
uvicorn api:app --reload
```

---

# API Documentation

* Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* OpenAPI: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

# License

This project is intended for educational purposes only and demonstrates ETL architecture, data validation systems, and backend data engineering workflows using Python.

```