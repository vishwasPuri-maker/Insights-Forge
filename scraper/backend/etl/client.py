import os
import json
import time
import logging
import requests
from datetime import datetime, timezone

# ==========================================================
# STRUCTURED LOGGER
# ==========================================================
class StructuredLogger:
    def __init__(self, name="backend-client"):
        self.name = name

    def _log(self, level, event, **kwargs):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "logger": self.name,
            "event": event,
            **kwargs
        }
        # Print JSON to console
        print(json.dumps(log_entry))
        
        # Log to file
        log_folder = "data/logs"
        os.makedirs(log_folder, exist_ok=True)
        try:
            with open(os.path.join(log_folder, "pipeline.log"), "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass

    def info(self, event, **kwargs):
        self._log("INFO", event, **kwargs)

    def warning(self, event, **kwargs):
        self._log("WARNING", event, **kwargs)

    def error(self, event, **kwargs):
        self._log("ERROR", event, **kwargs)


# ==========================================================
# ENV LOADER HELPER
# ==========================================================
def load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()


# ==========================================================
# BACKEND API CLIENT
# ==========================================================
class BackendApiClient:
    def __init__(self, api_url=None, email=None, password=None):
        self.logger = StructuredLogger()
        
        # Load env variables if not explicitly provided
        if not api_url or not email or not password:
            load_env()
            api_url = api_url or os.getenv("BACKEND_API_URL")
            email = email or os.getenv("SCRAPER_USER_EMAIL")
            password = password or os.getenv("SCRAPER_USER_PASSWORD")
            
        if not api_url or not email or not password:
            self.logger.error("config_missing", message="Missing API configuration or credentials in environment.")
            raise ValueError("Missing BACKEND_API_URL, SCRAPER_USER_EMAIL, or SCRAPER_USER_PASSWORD environment variables.")

        self.api_url = api_url
        self.email = email
        self.password = password
        self.access_token = None
        self.session = requests.Session()
        
        self.logger.info("client_initialized", api_url=self.api_url, email=self.email)

    def login(self, max_retries=3, backoff_factor=1.5):
        """Authenticates with the backend and stores the JWT access token in memory."""
        url = f"{self.api_url.rstrip('/')}/auth/login"
        payload = {
            "email": self.email,
            "password": self.password
        }
        
        self.logger.info("auth_attempt_started")
        
        for attempt in range(1, max_retries + 1):
            try:
                response = self.session.post(url, json=payload, timeout=10.0)
                
                # Check for successful response
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data.get("access_token")
                    if not self.access_token:
                        self.logger.error("auth_failed_token_missing", status=200)
                        return False
                        
                    # Cache the token in session headers
                    self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                    self.logger.info("auth_success", token_preview=self.access_token[:15] + "...")
                    return True
                    
                # Handle specific authentication failures
                elif response.status_code in (401, 403):
                    self.logger.error("auth_failed_invalid_credentials", status=response.status_code, response_body=response.text)
                    return False
                    
                # Server error / transient failure -> Retry
                elif response.status_code >= 500:
                    self.logger.warning("auth_transient_server_error", status=response.status_code, attempt=attempt)
                    if attempt == max_retries:
                        self.logger.error("auth_failed_max_retries_reached", error="Server error on login")
                        return False
                    time.sleep(backoff_factor ** attempt)
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning("auth_transient_network_error", error=str(e), attempt=attempt)
                if attempt == max_retries:
                    self.logger.error("auth_failed_max_retries_reached", error=str(e))
                    return False
                time.sleep(backoff_factor ** attempt)
                
        return False

    def request(self, method, path, max_retries=3, backoff_factor=1.5, **kwargs):
        """Wrapper around requests with timeout, retries, and token auto-refresh."""
        if not self.access_token:
            self.logger.warning("auth_token_not_found_attempting_login")
            if not self.login():
                raise RuntimeError("Authentication failed. Cannot perform request.")
                
        if "timeout" not in kwargs:
            kwargs["timeout"] = 10.0
            
        url = f"{self.api_url.rstrip('/')}/{path.lstrip('/')}"
        
        for attempt in range(1, max_retries + 1):
            try:
                # Seek all file pointers back to 0 if this is a retry attempt
                if attempt > 1 and "files" in kwargs:
                    for file_key, file_val in kwargs["files"].items():
                        if isinstance(file_val, tuple) and len(file_val) > 1:
                            fileobj = file_val[1]
                            if hasattr(fileobj, "seek"):
                                fileobj.seek(0)
                
                self.logger.info("request_sent", method=method, path=path, attempt=attempt)
                response = self.session.request(method, url, **kwargs)
                
                # Check for token expiration / invalidation -> re-login and retry once
                if response.status_code == 401:
                    self.logger.warning("token_expired_reauthenticating")
                    if self.login():
                        # Retry the request with new headers
                        response = self.session.request(method, url, **kwargs)
                    return response
                    
                # Server error -> retry
                if response.status_code >= 500:
                    self.logger.warning("request_transient_server_error", status=response.status_code, attempt=attempt)
                    if attempt == max_retries:
                        return response
                    time.sleep(backoff_factor ** attempt)
                    continue
                    
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning("request_transient_network_error", error=str(e), attempt=attempt)
                if attempt == max_retries:
                    raise e
                time.sleep(backoff_factor ** attempt)

    def upload_dataset(self, file_path, sector):
        """Validates and uploads a cleaned CSV dataset to the backend via the ingestion stream endpoint."""
        # 1. Pre-upload validations
        if not os.path.exists(file_path):
            self.logger.error("upload_validation_failed", error="file_not_found", file_path=file_path)
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if not file_path.lower().endswith(".csv"):
            self.logger.error("upload_validation_failed", error="invalid_extension", file_path=file_path)
            raise ValueError(f"File extension must be .csv: {file_path}")
            
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            self.logger.error("upload_validation_failed", error="file_empty", file_path=file_path)
            raise ValueError(f"File is empty: {file_path}")
            
        # 2. Checksum Generation (SHA-256)
        import hashlib
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        checksum = sha256.hexdigest()
        
        filename = os.path.basename(file_path)
        self.logger.info("file_checksum_generated", filename=filename, checksum=checksum, file_size=file_size)
        
        self.logger.info("upload_validation_success", file_path=file_path, file_size=file_size)
        self.logger.info("upload_started", file=filename, sector=sector)
        
        # 3. Read local CSV row count (excluding header)
        import csv
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            csv_rows = sum(1 for row in reader) - 1
            
        self.logger.info("local_row_count_calculated", file=filename, rows=csv_rows)
        
        # 4. Open file stream and execute request
        with open(file_path, "rb") as f:
            files = {
                "file": (filename, f, "text/csv")
            }
            data = {
                "sector": sector
            }
            try:
                response = self.request("POST", "ingestion/stream", files=files, data=data, timeout=60.0)
                
                # Handle response codes
                if response.status_code == 201:
                    res_json = response.json()
                    dataset_id = res_json.get("dataset_id")
                    self.logger.info("upload_completed", 
                                     dataset_id=dataset_id, 
                                     sector=res_json.get("sector"), 
                                     status=res_json.get("status"), 
                                     size_bytes=res_json.get("size_bytes"))
                    
                    # 5. Row Count Verification
                    self.logger.info("verification_started", dataset_id=dataset_id)
                    time.sleep(1.0) # Let the backend finish writing to DB
                    
                    db_response = self.request("GET", f"sectors/{sector}/records", params={"dataset_id": dataset_id, "limit": 1})
                    if db_response.status_code != 200:
                        self.logger.error("verification_failed_endpoint_error", status=db_response.status_code)
                        raise RuntimeError(f"Failed to query records count: {db_response.text}")
                        
                    db_rows = db_response.json().get("total")
                    if csv_rows != db_rows:
                        self.logger.error("row_count_mismatch", csv_rows=csv_rows, db_rows=db_rows)
                        raise ValueError(f"Row count mismatch: CSV has {csv_rows} rows, but database has {db_rows} records.")
                        
                    self.logger.info("row_count_verified", csv_rows=csv_rows, db_rows=db_rows, match=True)
                    return res_json
                else:
                    self.logger.error("upload_failed", 
                                      status=response.status_code, 
                                      response_body=response.text,
                                      file=filename)
                    response.raise_for_status()
            except Exception as e:
                self.logger.error("upload_unexpected_exception", error=str(e), file=filename)
                raise e

