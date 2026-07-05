import os
import pandas as pd

# Folder paths
RAW_FOLDER = "data/raw"
CLEAN_FOLDER = "data/cleaned"

# Create cleaned folder if it doesn't exist
os.makedirs(CLEAN_FOLDER, exist_ok=True)

# Loop through every file in raw folder
for file in os.listdir(RAW_FOLDER):

    # Process only CSV files
    if file.endswith(".csv"):

        file_path = os.path.join(RAW_FOLDER, file)

        print(f"Processing: {file}")

        # Read CSV
        df = pd.read_csv(file_path)

        # ----------------------
        # DATA CLEANING
        # ----------------------

        # Remove duplicate rows
        df = df.drop_duplicates()

        # Remove completely empty rows
        df = df.dropna(how="all")

        # Clean column names
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        # Remove extra spaces from text columns
        for column in df.select_dtypes(include="object").columns:
            df[column] = df[column].astype(str).str.strip()

        # Fill missing values
        df = df.fillna("Unknown")

        # ----------------------
        # SAVE CLEAN FILE
        # ----------------------

        filename = file.replace(".csv", "_clean.csv")

        output_path = os.path.join(CLEAN_FOLDER, filename)

        df.to_csv(output_path, index=False)

        print(f"Saved: {filename}")

print("\nAll datasets cleaned successfully!")