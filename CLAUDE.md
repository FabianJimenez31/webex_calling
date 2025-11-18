# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Webex Calling Security AI** is an AI-powered security and anomaly detection system for Webex Calling deployments. It combines real-time call monitoring, machine learning-based fraud detection, and Claude AI analysis to identify security threats, unusual calling patterns, and policy violations.

The system is designed for **Davivienda** (Colombian bank) with custom branding and has both backend API and frontend dashboard components.

## Architecture

### Backend (FastAPI + Python)
- **FastAPI 0.109.0** REST API with async support
- **Database**: SQLite (dev) / PostgreSQL 15 (prod) with SQLAlchemy 2.0 async ORM
- **AI Analysis**: OpenRouter API (GPT OSS Safeguard 20B model) via `anomaly_detector.py`
- **ML Detection**: scikit-learn Isolation Forest for international call anomalies
- **OAuth 2.0**: Three-legged flow for Webex integration with auto-refresh
- **Scheduler**: APScheduler for automated analysis jobs (hourly/daily/custom)

### Frontend (React + TypeScript)
- **React 19** with **TypeScript** and **Vite 7**
- **Styling**: Tailwind CSS 3.4 with Davivienda theme
- **Components**: shadcn/ui with custom Davivienda components
- **Theme Colors**:
  - Primary Red: `#E30519`
  - Black: `#010101`
  - Light Gray: `#F5F5F5`

### Key Services
1. **CDR Ingestion** (`webex_client.py`): Fetches Call Detail Records from Webex analytics API
2. **Recordings Processing** (`webex_recordings.py`, `recording_processor.py`): Complete pipeline for Webex Calling recordings - download audio, extract transcripts, generate AI summaries, detect language, analyze sentiment
3. **Anomaly Detection** (`anomaly_detector.py`): AI-powered threat analysis using OpenRouter
4. **Fraud Detection** (`fraud_detection.py`): Rule-based detection (international calls, after-hours, mass dialing, call forwarding)
5. **Chat Assistant** (`chat_assistant.py`): Natural language interface for querying CDR data
6. **Alert Service** (`alert_service.py`): Webhook notifications (Slack/Teams) and email alerts
7. **Report Generator** (`report_generator.py`): PDF/CSV export with Davivienda branding

## Common Commands

### Backend Development

```bash
# Start backend server (development with auto-reload)
cd webex_calling
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python -m uvicorn src.main:app --reload --port 8000

# Run tests
pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_anomaly_detector.py -v

# Code formatting and linting
make format  # black + isort
make lint    # flake8 + mypy
```

### Frontend Development

```bash
# Start frontend dev server
cd webex_calling/frontend
npm run dev  # Runs on http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview

# Lint TypeScript
npm run lint
```

### Docker Deployment

```bash
# Start all services (PostgreSQL + FastAPI + pgAdmin)
docker-compose up -d

# View logs
docker logs webex-calling-api -f

# Stop services
docker-compose down

# Reset database (WARNING: deletes all data)
docker-compose down -v
```

### Database Management

```bash
# Initialize database (creates all tables)
python scripts/init_db.py

# SQLite database location (development)
# Path: webex_calling/webex_calling.db

# Access PostgreSQL (if using Docker)
psql -h localhost -U postgres -d webex_calling_security
```

## API Architecture

### Route Organization
All routes are in `src/api/routes/`:
- `alerts.py` - Alert CRUD, configuration, and history
- `cdrs.py` - CDR fetching and analysis
- `detection.py` - Anomaly detection and scheduler management
- `analytics.py` - Dashboard metrics and statistics
- `chat.py` - Natural language chat assistant
- `reports.py` - PDF/CSV report generation
- `auth.py` - Webex OAuth 2.0 flow

### Key Endpoints

**Authentication**:
- `GET /auth/login` - Initiate OAuth flow
- `GET /auth/callback` - OAuth callback handler
- `GET /auth/status` - Check token status

**CDRs**:
- `GET /api/v1/cdrs/` - Fetch CDRs from Webex (rate limit: 1/min)
- `GET /api/v1/cdrs/analyze` - Analyze stored CDRs

**Detection**:
- `POST /api/v1/detection/analyze` - Run anomaly detection
- `GET /api/v1/detection/analyze/quick` - Quick analysis endpoint
- `POST /api/v1/detection/schedule/enable` - Configure scheduled analysis
- `GET /api/v1/detection/schedule/jobs` - List scheduled jobs

**Chat Assistant**:
- `POST /api/v1/chat/ask` - Ask questions in natural language
- `GET /api/v1/chat/examples` - Get example questions

**Reports**:
- `GET /api/v1/reports/security/pdf` - Security report PDF
- `GET /api/v1/reports/security/csv` - Security report CSV

**Alerts**:
- `GET /api/v1/alerts` - List alerts with filtering
- `POST /api/v1/alerts/config/webhooks` - Configure webhooks (Slack/Teams)

## Data Models

### Database Schema
Located in `src/models/`:
- `cdr.py` - CDR and CallJourney models
- `user.py` - User/Extension model with risk scoring
- `alert.py` - Alert model with severity and status tracking

**CDR Model** (`call_detail_records` table):
- Stores all call records from Webex
- Fields: call_id, start_time, duration, calling_number, called_number, call_type, location, queue_name, trunk_name
- JSONB metadata field for flexible data

**Alert Model** (`alerts` table):
- Tracks security alerts and incidents
- Severity levels: LOW, MEDIUM, HIGH, CRITICAL
- Status: open, investigating, resolved
- Includes AI analysis field from Claude

## Detection Algorithms

### 1. Unusual International Calls (`international_calls.py`)
- **Algorithm**: Isolation Forest (scikit-learn)
- **Baseline**: 30-day user calling pattern
- **Triggers**: Anomaly score < -0.5 (default threshold)
- **Use case**: Detect compromised extensions making fraud calls

### 2. After-Hours Activity (`after_hours.py`)
- **Algorithm**: Rule-based with business hours configuration
- **Configuration**: Per-location business hours in `.env`
- **Triggers**: Calls outside defined business hours
- **Severity**: Based on frequency and time deviation

### 3. Mass Dialing Detection (`mass_dialing.py`)
- **Algorithm**: Pattern matching (high volume + short duration)
- **Default threshold**: 50 calls in 60 minutes
- **Triggers**: Autodialer patterns indicating PBX fraud
- **Severity**: CRITICAL for active fraud patterns

### 4. Call Forwarding Monitoring (`call_forwarding.py`)
- **Algorithm**: Configuration change tracking
- **Triggers**: After-hours changes, forwarding to external numbers
- **Use case**: Prevent SIM swapping and account takeover

## Webex Integration

### OAuth Flow
1. User visits `/auth/login` → redirected to Webex authorization
2. Webex callback to `/auth/callback` with authorization code
3. Backend exchanges code for access + refresh tokens
4. Tokens stored in `.webex_tokens.json` (persisted across restarts)
5. Auto-refresh implemented in `webex_oauth.py`

**Required Scopes**:
- `spark-admin:calling_cdr_read` - Read CDRs with full phone numbers
- `spark-admin:recordings_read` - Read Webex Calling recordings
- `spark-admin:recordings_write` - Delete recordings (optional)
- `analytics:read_all` - Access analytics API
- `spark:organizations_read` - Read org info
- `spark:people_read` - Read user info

### CDR API Details
- **Endpoint**: `analytics.webexapis.com/v1/cdr_feed`
- **Rate Limit**: 1 request per minute (enforced by Webex)
- **Latency**: CDRs available 5 minutes after call ends
- **Retention**: 48 hours in API (store in DB for longer retention)

## Recordings Module

### Overview
Complete pipeline for processing Webex Calling recordings with automated transcription, summarization, and analysis.

**Files**: `src/services/webex_recordings.py`, `src/services/recording_processor.py`, `src/models/recording.py`, `src/api/routes/recordings.py`

### Processing Pipeline
1. **Fetch** - List recordings from Webex Converged Recordings API
2. **Download** - Audio files and VTT transcripts (if available)
3. **Transcribe** - Extract text from Webex VTT or use external STT (Whisper, Google)
4. **Summarize** - Generate AI summaries with key points, topics, action items
5. **Analyze** - Sentiment analysis and language detection
6. **Store** - Consolidated data in `recordings` table

### Key Endpoints
- `POST /api/v1/recordings/fetch` - Fetch and process new recordings from Webex
- `GET /api/v1/recordings/` - List recordings with filters (status, date range)
- `GET /api/v1/recordings/{id}` - Get recording details
- `POST /api/v1/recordings/{id}/reprocess` - Reprocess a recording
- `GET /api/v1/recordings/stats/summary` - Statistics dashboard

### Storage Structure
```
data/
├── recordings/YYYY/MM/DD/{recording_id}.mp3  # Audio files
└── transcripts/YYYY/MM/DD/{recording_id}.vtt # Transcript files
```

### Role Requirements
**CRITICAL**: Converged Recordings API requires user to have one of these Webex roles:
- **Full Administrator** (recommended)
- **Compliance Officer** (with `spark-compliance:recordings_read` scope)
- Regular users will get 403 Forbidden even with correct scopes

See `RECORDINGS_ACCESS_ISSUE.md` for troubleshooting access problems.

### Documentation
- **Setup Guide**: `RECORDINGS_SETUP_GUIDE.md`
- **Usage Guide**: `RECORDINGS_MODULE_GUIDE.md`
- **Access Troubleshooting**: `RECORDINGS_ACCESS_ISSUE.md`
- **Verification Script**: `scripts/verify_recordings_access.py`

## AI Integration

### OpenRouter Configuration
- **Provider**: OpenRouter (openrouter.ai)
- **Model**: `openai/gpt-oss-safeguard-20b`
- **Purpose**: Analyze CDR patterns and generate security insights
- **Implementation**: `src/services/anomaly_detector.py`

### Claude Integration (Planned)
- Environment variable: `ANTHROPIC_API_KEY`
- Use Anthropic SDK (`anthropic==0.39.0`)
- For advanced threat analysis and natural language reporting

## Environment Configuration

**Critical variables** (see `.env.example`):
```bash
# Webex OAuth (primary authentication method)
WEBEX_CLIENT_ID=...
WEBEX_CLIENT_SECRET=...
WEBEX_REDIRECT_URI=http://localhost:8000/auth/callback

# Database (SQLite auto-used in dev, PostgreSQL in prod)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=webex_calling_security

# AI Services
ANTHROPIC_API_KEY=...  # For Claude AI features

# Detection Thresholds (tunable)
INTERNATIONAL_CALLS_THRESHOLD=5
MASS_DIALING_THRESHOLD=50
MASS_DIALING_TIME_WINDOW_MINUTES=60
```

## Testing

### Test Structure
```
tests/
├── unit/           # Unit tests for individual functions
└── integration/    # Integration tests for API endpoints
```

### Running Tests
```bash
# All tests with coverage report
pytest tests/ -v --cov=src --cov-report=html

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_international_calls.py -v

# Coverage report opens in browser
open htmlcov/index.html
```

## Scheduler System

The scheduler (`src/services/scheduler.py`) uses APScheduler for automated analysis:

**Schedule Types**:
1. **Hourly**: `{"schedule_type": "hourly", "hours": 1}`
2. **Daily**: `{"schedule_type": "daily", "hour": 8, "minute": 0}`
3. **Custom**: `{"schedule_type": "custom", "interval_minutes": 30}`

**Lifecycle**:
- Started/stopped automatically with FastAPI lifespan events
- Jobs persist in memory (not database yet)
- Configurable via `/api/v1/detection/schedule/enable` endpoint

## Frontend Components

**Davivienda Components** (`src/components/davivienda/`):
- `MainDashboard.tsx` - Main security dashboard
- `SecurityDashboard.tsx` - Security alerts and threats
- `ChatAssistant.tsx` - Natural language query interface
- `ReportsPanel.tsx` - Report generation interface
- `SchedulerPanel.tsx` - Scheduled analysis configuration
- `AgentPerformanceDashboard.tsx` - Agent metrics
- `SLAComplianceView.tsx` - SLA tracking

**UI Components** (`src/components/ui/`):
- shadcn/ui components styled with Davivienda theme

## Real Data Context

**Current Deployment**:
- Organization: ITS INFOCOMUNICACION SAS
- Primary Location: PoC Banco Davivienda (Colombia)
- Additional Locations: 7 total (Costa Rica, Guatemala, El Salvador, Denver, etc.)
- Test Data: 167+ real CDR records processed
- Primary Queue: "NA" (108 calls, 64.6% of traffic)

## Code Quality

### Pre-commit Hooks
Configured in `.pre-commit-config.yaml`:
- black (code formatting)
- flake8 (linting)
- mypy (type checking)

### Style Guidelines
- **Line length**: 100 characters (black + flake8)
- **Import sorting**: isort with black profile
- **Type hints**: Required for public functions
- **Docstrings**: Required for classes and public methods

## Troubleshooting

### Backend won't start
- Check if port 8000 is available: `lsof -i :8000`
- Verify virtual environment is activated
- Check database connection (falls back to SQLite if PostgreSQL unavailable)

### Frontend won't start
- Check if port 5173 is available
- Verify Node.js version (requires Node 18+)
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

### OAuth errors
- Verify redirect URI matches Webex app configuration exactly
- Check scopes match required permissions
- Delete `.webex_tokens.json` to force re-authentication

### Rate limit errors (CDR API)
- Webex enforces 1 request/minute limit
- Implement exponential backoff in `webex_client.py`
- Consider caching recent CDR responses

### Database errors
- Development mode auto-creates SQLite database
- Production requires PostgreSQL running (Docker: `docker-compose up postgres`)
- Reset database: `rm webex_calling.db` (dev) or `docker-compose down -v` (prod)

## Important Notes

1. **Rate Limits**: Webex CDR API is strictly rate-limited to 1 request/minute. Always respect this limit.

2. **Token Persistence**: OAuth tokens are stored in `.webex_tokens.json` in the project root. This file is gitignored but critical for operation. Back it up in production.

3. **Database Flexibility**: The system works with SQLite (dev) or PostgreSQL (prod). Database initialization is non-blocking - the API will start even if DB is unavailable (with limited functionality).

4. **AI Model Configuration**: Currently using OpenRouter, not direct Anthropic API. To switch to Claude, modify `anomaly_detector.py` to use the Anthropic SDK.

5. **Davivienda Branding**: All user-facing components must use official colors (#E30519, #010101, #F5F5F5). PDFs use ReportLab for branding.

6. **Security**: Never commit `.env` file or `.webex_tokens.json`. Use `.env.example` as template.

7. **Timezone**: Default timezone is America/Bogota (UTC-5). After-hours detection uses local business hours per location.
