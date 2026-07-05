| Module | Endpoint | Method | Auth | Input | Output | Purpose |
| ------ | -------- | ------ | ---- | ----- | ------ | ------- |
| health | /api/v1/health | GET | No | None | JSON | Health |
| auth | /api/v1/auth/signup | POST | No | Body | None | Signup |
| auth | /api/v1/auth/login | POST | No | Body | JSON | Login |
| auth | /api/v1/auth/refresh | POST | No | Body | JSON | Refresh |
| auth | /api/v1/auth/logout | POST | No | Body | None | Logout |
| ingestion | /api/v1/ingestion/stream | POST | Yes | Body | None | Stream Upload |
| datasets | /api/v1/datasets | GET | Yes | Params | JSON | List Datasets |
| datasets | /api/v1/datasets/{dataset_id} | GET | Yes | Params | JSON | Get Dataset |
| sectors | /api/v1/sectors/{sector}/scorecard | GET | Yes | Params | JSON | Scorecard |
| sectors | /api/v1/sectors/{sector}/timeseries | GET | Yes | Params | JSON | Timeseries |
| sectors | /api/v1/sectors/{sector}/records | GET | Yes | Params | JSON | List Records |
| sectors | /api/v1/sectors/{sector}/geo | GET | Yes | Params | JSON | Geo |
| sectors | /api/v1/sectors/{sector}/records/{record_id} | GET | Yes | Params | JSON | Get Record |
| decision-cards | /api/v1/decision-cards | GET | Yes | Params | JSON | List Decision Cards |
| decision-cards | /api/v1/decision-cards/{card_id}/approve | POST | Yes | Params | JSON | Approve |
| decision-cards | /api/v1/decision-cards/{card_id}/reject | POST | Yes | Params | JSON | Reject |
| simulate | /api/v1/simulate | POST | Yes | Body | JSON | Simulate |
| reports | /api/v1/reports/compile | POST | Yes | Body | None | Compile Report |
| reports | /api/v1/reports/{report_id} | GET | Yes | Params | JSON | Get Report |
| thresholds | /api/v1/thresholds | GET | Yes | None | JSON | List Thresholds |
| thresholds | /api/v1/thresholds/{threshold_id} | PUT | Yes | Body | JSON | Update Threshold |
| users | /api/v1/users | GET | Yes | None | JSON | List Users |
| users | /api/v1/users | POST | Yes | Body | None | Create User |
| users | /api/v1/users/{user_id} | DELETE | Yes | Params | None | Delete User |