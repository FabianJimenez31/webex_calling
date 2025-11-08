# Webex Calling Security AI

AI-powered security and anomaly detection system for Webex Calling, using Claude Agent SDK for intelligent threat analysis.

## 🎯 Overview

This system provides real-time security monitoring and anomaly detection for Webex Calling deployments, helping organizations:

- Detect unusual calling patterns that may indicate fraud or security breaches
- Identify compromised extensions or unauthorized usage
- Ensure compliance with security policies and regulations
- Generate intelligent alerts and recommendations using Claude AI

## 🚀 Features

### Implemented Detection Modules

1. **Unusual International Calls Detection**
   - Uses Isolation Forest ML algorithm to detect anomalous international calling patterns
   - Establishes user baseline behavior over 30 days
   - Alerts on significant deviations from normal patterns

2. **After-Hours Activity Detection**
   - Monitors calling activity outside business hours by location
   - Configurable business hours per location (Bogota, Mexico, Madrid)
   - Severity-based alerting system

3. **Mass Dialing Detection**
   - Identifies potential PBX fraud or compromised extensions
   - Detects autodialer patterns (high volume, short duration calls)
   - Critical severity for patterns indicating active fraud

4. **Suspicious Call Forwarding Detection**
   - Monitors configuration changes to call forwarding settings
   - Flags after-hours changes or forwarding to external numbers
   - Helps prevent SIM swapping and account compromise attacks

## 📋 Requirements

- Python 3.10+
- PostgreSQL 12+ (for CDR storage)
- Webex Calling with admin API access
- Anthropic API key (for Claude integration)

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd webex-calling-security-ai
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Required environment variables:
- `WEBEX_ACCESS_TOKEN` - Your Webex admin access token
- `WEBEX_ORG_ID` - Your organization ID
- `ANTHROPIC_API_KEY` - Your Claude API key
- Database credentials

### 5. Initialize database

```bash
# TODO: Add database migration commands
python scripts/init_db.py
```

## 📊 Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Webex Calling CDR API                                   │
│  (Detailed Call History - every 5 min)                   │
└────────────────┬─────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────┐
│  INGESTION LAYER                                         │
│  • Fetch CDR data                                        │
│  • Normalize and enrich                                  │
│  • Store in PostgreSQL                                   │
└────────────────┬─────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────┐
│  DETECTION LAYER (src/detectors/)                        │
│  • International calls (ML)                              │
│  • After-hours activity (Rule-based)                     │
│  • Mass dialing (Pattern matching)                       │
│  • Call forwarding (Config monitoring)                   │
└────────────────┬─────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────┐
│  CLAUDE AI ANALYSIS                                      │
│  • Contextual threat assessment                          │
│  • Severity evaluation                                   │
│  • Recommended actions                                   │
│  • Natural language reports                              │
└────────────────┬─────────────────────────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────┐
│  ALERTING LAYER                                          │
│  • Webex Bot notifications                               │
│  • Email alerts                                          │
│  • Slack integration                                     │
│  • Dashboard (Grafana)                                   │
└──────────────────────────────────────────────────────────┘
```

## 🔧 Usage

### Run detection modules

```python
from src.detectors import (
    detect_unusual_international_calls,
    detect_after_hours_activity,
    detect_mass_dialing,
    detect_suspicious_call_forwarding
)

# Connect to database
db = connect_to_database()

# Run detection
intl_anomalies = detect_unusual_international_calls(db, user_id="user123")
after_hours = detect_after_hours_activity(db)
mass_dial = detect_mass_dialing(db)
fwd_suspicious = detect_suspicious_call_forwarding(webex_api)
```

### Using Claude Code commands

```bash
# Setup development environment
/setup

# Run tests
/test

# Analyze CDR data
/analyze-cdr
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test module
pytest tests/unit/test_international_calls.py
```

## 📁 Project Structure

```
webex-calling-security-ai/
├── .claude/                    # Claude Code configuration
│   ├── commands/               # Custom Claude commands
│   └── settings.local.json     # Project-specific settings
├── src/
│   ├── detectors/              # Anomaly detection modules
│   │   ├── international_calls.py
│   │   ├── after_hours.py
│   │   ├── mass_dialing.py
│   │   └── call_forwarding.py
│   ├── ingestion/              # CDR data ingestion (TODO)
│   ├── models/                 # Data models (TODO)
│   ├── alerting/               # Alert system (TODO)
│   └── utils/                  # Utilities
│       └── logger.py
├── tests/
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── config/                     # Configuration files
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── data/
│   ├── raw/                    # Raw CDR data
│   ├── processed/              # Processed data
│   └── models/                 # Trained ML models
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🔐 Security Metrics Tracked

- Daily international calls by destination country
- After-hours activity rate (% of calls outside business hours)
- Average call duration by type (detect abnormally short calls)
- Failed authentication attempts
- Configuration changes after hours
- PCI DSS violations (calls to payment lines without encryption)
- GDPR compliance (international calls to EU from unauthorized users)
- SOX audit trail (complete CDR retention for 7 years)

## 🎯 Roadmap

### Phase 1: Core Detection (Current)
- [x] International calls detection
- [x] After-hours activity detection
- [x] Mass dialing detection
- [x] Call forwarding monitoring
- [ ] CDR ingestion pipeline
- [ ] Database schema and models

### Phase 2: Intelligence & Alerting
- [ ] Claude AI integration for threat analysis
- [ ] Webex Bot for notifications
- [ ] Email alerting system
- [ ] Slack integration
- [ ] Alert suppression and deduplication

### Phase 3: Visualization & Reporting
- [ ] Grafana dashboard
- [ ] Custom reporting engine
- [ ] Executive summaries (auto-generated by Claude)
- [ ] Compliance reports (ISO, SOX, PCI DSS)

### Phase 4: Advanced Features
- [ ] Call journey reconstruction
- [ ] Predictive analytics
- [ ] User behavior analytics (UEBA)
- [ ] Integration with SIEM (Splunk, QRadar)
- [ ] API for external integrations

## 📖 Documentation

- [Architecture Overview](docs/architecture.md) (TODO)
- [Detection Algorithms](docs/algorithms.md) (TODO)
- [API Reference](docs/api.md) (TODO)
- [Deployment Guide](docs/deployment.md) (TODO)

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## 📄 License

[Your License Here]

## 🙋 Support

For questions or issues, please contact:
- Email: [your-email]
- Slack: [your-slack-channel]

## 🙏 Acknowledgments

- Built with [Claude Agent SDK](https://docs.claude.com/en/docs/agent-sdk/overview) by Anthropic
- Uses Webex Calling APIs for CDR access
- Powered by scikit-learn for machine learning

---

**Note**: This project is in active development. Some features are still being implemented (marked as TODO).
