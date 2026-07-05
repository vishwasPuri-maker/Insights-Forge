import os
import time
import pandas as pd
import sys
import json
from datetime import datetime, timezone

# Ensure etl folder is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from etl.client import BackendApiClient, StructuredLogger

CLEAN_FOLDER = "data/cleaned"
SECTOR = "retail"  # Scoped to authenticated tenant's sector

def load_and_upload():
    logger = StructuredLogger("etl-loader")
    logger.info("etl_load_started", folder=CLEAN_FOLDER)
    
    try:
        client = BackendApiClient()
        if not client.login():
            logger.error("etl_load_auth_failed", message="Could not authenticate with backend.")
            sys.exit(1)
    except Exception as e:
        logger.error("etl_load_init_failed", error=str(e))
        sys.exit(1)

    successful_uploads = []
    failed_uploads = []
    skipped_uploads = []

    files = [f for f in os.listdir(CLEAN_FOLDER) if f.endswith(".csv")]
    
    total_records = 0
    total_size = 0
    total_upload_duration = 0.0

    for file in files:
        file_path = os.path.join(CLEAN_FOLDER, file)
        file_size = os.path.getsize(file_path)
        
        # Read local row count (excluding header)
        try:
            df = pd.read_csv(file_path)
            csv_rows = len(df)
        except Exception as e:
            logger.error("read_csv_failed", file=file, error=str(e))
            failed_uploads.append({"file": file, "reason": f"Read CSV failed: {str(e)}"})
            continue

        # Checksum Generation (SHA-256)
        import hashlib
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            checksum = sha256.hexdigest()
        except Exception as e:
            logger.error("checksum_generation_failed", file=file, error=str(e))
            failed_uploads.append({"file": file, "reason": f"Checksum generation failed: {str(e)}"})
            continue

        # Optional: check if file is empty
        if file_size == 0 or csv_rows == 0:
            logger.warning("skipping_empty_file", file=file)
            skipped_uploads.append({"file": file, "reason": "File is empty"})
            continue

        # Trigger Ingestion Upload
        logger.info("pipeline_dataset_upload_started", file=file, size=file_size, rows=csv_rows)
        start_time = time.time()
        
        try:
            # Execute upload & row-count validation
            res = client.upload_dataset(file_path, SECTOR)
            duration = time.time() - start_time
            
            successful_uploads.append({
                "file": file,
                "dataset_id": res.get("dataset_id"),
                "rows": csv_rows,
                "size_bytes": file_size,
                "duration_sec": round(duration, 2),
                "checksum": checksum
            })
            
            total_records += csv_rows
            total_size += file_size
            total_upload_duration += duration
            
            logger.info("pipeline_dataset_upload_success", file=file, dataset_id=res.get("dataset_id"), duration=duration)
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error("pipeline_dataset_upload_failed", file=file, error=str(e), duration=duration)
            failed_uploads.append({
                "file": file,
                "reason": str(e),
                "duration_sec": round(duration, 2)
            })

    # Summary calculations
    avg_speed = 0.0
    if total_upload_duration > 0:
        avg_speed = round((total_size / (1024 * 1024)) / total_upload_duration, 4) # MB/s

    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_datasets": len(files),
        "successful_count": len(successful_uploads),
        "failed_count": len(failed_uploads),
        "skipped_count": len(skipped_uploads),
        "total_records_ingested": total_records,
        "total_size_bytes": total_size,
        "total_upload_duration_sec": round(total_upload_duration, 2),
        "average_upload_speed_mb_s": avg_speed,
        "successful_uploads": successful_uploads,
        "failed_uploads": failed_uploads,
        "skipped_uploads": skipped_uploads
    }

    # Write summary to a JSON file for metrics reporting
    metrics_path = "data/logs/etl_summary.json"
    with open(metrics_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Console Summary prints
    print("\n" + "="*50)
    print("         ETL PIPELINE LOAD SUMMARY")
    print("="*50)
    print(f"Total Cleaned Files : {len(files)}")
    print(f"Successful Uploads  : {len(successful_uploads)}")
    print(f"Failed Uploads      : {len(failed_uploads)}")
    print(f"Skipped Uploads     : {len(skipped_uploads)}")
    print(f"Total Records       : {total_records}")
    print(f"Total Size Ingested : {total_size / (1024*1024):.2f} MB")
    print(f"Avg Upload Speed    : {avg_speed:.4f} MB/s")
    print("="*50)
    
    if failed_uploads:
        print("\nFailed Uploads Details:")
        for f in failed_uploads:
            print(f"  - {f['file']}: {f['reason']}")
    print("="*50 + "\n")

if __name__ == "__main__":
    load_and_upload()