# SecureLens Architecture

## High Level Workflow

User
↓
Submit Website URL
↓
Backend API
↓
Scan Queue
↓
Scanner Workers
↓
Results Database
↓
AI Analysis Layer
↓
Report Generator
↓
Dashboard

---

## Components

### Frontend

Technology:
- Next.js
- Tailwind CSS

Responsibilities:
- Authentication
- Dashboard
- Scan Submission
- Report Viewer

### Backend

Technology:
- FastAPI

Responsibilities:
- User Management
- Scan Management
- API Endpoints

### Database

Technology:
- PostgreSQL

Responsibilities:
- Users
- Websites
- Findings
- Reports

### Scanner Engine

Technology:
- Python

Responsibilities:
- SSL Analysis
- Security Header Checks
- Technology Detection
- Vulnerability Detection

### AI Layer

Responsibilities:
- Risk Prioritization
- Vulnerability Explanation
- Remediation Suggestions
