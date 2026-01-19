# Power Automate JSON Processor

A demo project that uploads weather data to OneDrive and triggers automated email/push notifications via Power Automate.

## What It Does

```
Python Script                         Power Automate
┌──────────────────┐                 ┌─────────────────────────────────┐
│                  │                 │                                 │
│  Generate JSON   │────upload──────▶│  Trigger: New file detected     │
│  weather data    │                 │      │                          │
│                  │                 │      ▼                          │
└──────────────────┘                 │  Parse JSON content             │
                                     │      │                          │
                                     │      ├──────▶ Send Gmail        │
                                     │      │                          │
                                     │      └──────▶ Push notification │
                                     │                                 │
                                     └─────────────────────────────────┘
```

## Project Structure

```
power-automate-demo/
├── auth.py        # Microsoft OAuth authentication
├── onedrive.py    # OneDrive upload via Graph API
├── main.py        # Generates weather data, triggers upload
├── .env           # Your credentials (not in repo)
└── .gitignore
```

## Setup

### 1. Azure App Registration

1. Go to [Azure Portal](https://portal.azure.com) → App registrations → New registration
2. Name: `PowerAutomate-JSONUploader`
3. Account type: "Accounts in any organizational directory and personal Microsoft accounts"
4. Redirect URI: Web → `http://localhost:8000/callback`
5. After creation, go to "Certificates & secrets" → New client secret
6. Go to "API permissions" → Add permission → Microsoft Graph → Delegated:
   - `Files.ReadWrite`
   - `Files.ReadWrite.All`

Save these values:
- Application (client) ID
- Client secret value

### 2. Python Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install msal requests python-dotenv
```

### 3. Configuration

Create `.env` file:

```
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
TENANT_ID=your_tenant_id
```

### 4. Power Automate Flow

Create a cloud flow at [make.powerautomate.com](https://make.powerautomate.com):

| Step | Action | Configuration |
|------|--------|---------------|
| 1 | When a file is created (OneDrive) | Folder: Apps/PowerAutomate-JSONUploader |
| 2 | Get file content | File: File identifier from step 1 |
| 3 | Compose | `base64ToString(body('Get_file_content').$content)` |
| 4 | Parse JSON | Content: Outputs from step 3 |
| 5 | Send email (Gmail) | Subject: `Weather Report - [report_generated_at]` |
| 6 | Send mobile notification | Text: `New weather report: [File name]` |

Parse JSON schema:
```json
{
  "type": "object",
  "properties": {
    "report_generated_at": { "type": "string" },
    "total_records": { "type": "integer" },
    "data": { "type": "array" }
  }
}
```

## Usage

```bash
python main.py
```

First run opens a browser for Microsoft login. Subsequent runs use cached credentials.

Output:
```
Generating weather data...
Generated 10 records
Uploading weather_report_20260119_112415.json to OneDrive...
Using cached token
Successfully uploaded: weather_report_20260119_112415.json
```

Within seconds, you'll receive:
- Email with weather report summary
- Push notification on Power Automate mobile app

## Sample Data

```json
{
  "report_generated_at": "2026-01-19T11:24:15.688986",
  "total_records": 10,
  "data": [
    {
      "timestamp": "2026-01-19T11:24:15.688986",
      "city": "New York",
      "temperature_celsius": 24.0,
      "humidity_percent": 82,
      "wind_speed_kmh": 27.9,
      "condition": "Rainy"
    }
  ]
}
```

## Requirements

- Python 3.7+
- Personal Microsoft account with OneDrive
- Power Automate account (organizational)
- Gmail account
- Power Automate mobile app (for push notifications)