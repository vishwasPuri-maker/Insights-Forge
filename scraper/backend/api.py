from fastapi import FastAPI, HTTPException
import pandas as pd
import os

# ==========================================================
# FastAPI Configuration
# ==========================================================

app = FastAPI(
    title="Government ETL Pipeline API",
    description="REST API for accessing cleaned government datasets generated through the ETL Pipeline.",
    version="1.0.0"
)

# ==========================================================
# Folder Paths
# ==========================================================

DATA_FOLDER = "data/cleaned"

# ==========================================================
# Helper Function
# ==========================================================

def load_dataset(filename: str):

    file_path = os.path.join(DATA_FOLDER, filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"{filename} not found."
        )

    try:

        df = pd.read_csv(file_path)

        df = df.where(pd.notnull(df), None)

        return {
            "dataset": filename,
            "total_records": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "data": df.to_dict(orient="records")
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================================
# Home
# ==========================================================

@app.get("/")
def home():

    return {
        "project": "Government ETL Pipeline",
        "status": "Running",
        "version": "1.0.0",
        "available_endpoints": [
            "/health",
            "/datasets",
            "/education",
            "/employment",
            "/government",
            "/healthcare",
            "/agriculture",
            "/scraped"
        ]
    }


# ==========================================================
# Health Check
# ==========================================================

@app.get("/health")
def health():

    return {
        "status": "Healthy",
        "api": "Running Successfully"
    }


# ==========================================================
# Dataset List
# ==========================================================

@app.get("/datasets")
def datasets():

    files = []

    if os.path.exists(DATA_FOLDER):

        for file in os.listdir(DATA_FOLDER):

            if file.endswith(".csv"):
                files.append(file)

    return {
        "available_datasets": files,
        "total_datasets": len(files)
    }


# ==========================================================
# Education Dataset
# ==========================================================

@app.get("/education")
def education():

    return load_dataset("education_clean.csv")


# ==========================================================
# Employment Dataset
# ==========================================================

@app.get("/employment")
def employment():

    return load_dataset("employment_clean.csv")


# ==========================================================
# Government Schemes Dataset
# ==========================================================

@app.get("/government")
def government():

    return load_dataset("government_schemes_clean.csv")


# ==========================================================
# Healthcare Dataset
# ==========================================================

@app.get("/healthcare")
def healthcare():

    return load_dataset("healthcare_dataset_clean.csv")


# ==========================================================
# Agriculture Dataset
# ==========================================================

@app.get("/agriculture")
def agriculture():

    return load_dataset("india_agriculture_crop_production_clean.csv")


# ==========================================================
# Scraped Dataset
# ==========================================================

@app.get("/scraped")
def scraped():

    return load_dataset("scraped_clean.csv")