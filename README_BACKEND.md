

# 🚀 Webex Calling Security AI - Backend (FastAPI + PostgreSQL)

Backend API para detección de anomalías y seguridad en Webex Calling.

## 📋 Stack Tecnológico

- **Framework:** FastAPI 0.109.0
- **Base de Datos:** PostgreSQL 15
- **ORM:** SQLAlchemy 2.0 (async)
- **Validación:** Pydantic v2
- **ML:** scikit-learn, Prophet
- **IA:** Claude Agent SDK (Anthropic)
- **APIs:** Webex Calling, Webex Teams

---

## 🏗️ Arquitectura

```
┌────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints (REST)                                 │  │
│  │  /api/v1/alerts, /api/v1/cdr, /api/v1/detection     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────┬──────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│              Business Logic Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │  Detectors  │  │  Ingestion  │  │  Claude AI       │   │
│  │  (Anomalies)│  │  (CDR Pull) │  │  (Analysis)      │   │
│  └─────────────┘  └─────────────┘  └──────────────────┘   │
└─────────────────────┬──────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│              Data Layer (SQLAlchemy)                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Models: CDR, CallJourney, User, Alert             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬──────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│                   PostgreSQL Database                       │
│  Tables: call_detail_records, call_journeys, users, alerts │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Opción 1: Docker Compose (Recomendado)

```bash
# 1. Copiar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 2. Levantar servicios
docker-compose up -d

# 3. Verificar que esté corriendo
curl http://localhost:8000/health

# 4. Acceder a la documentación
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

**Servicios levantados:**
- FastAPI: http://localhost:8000
- PostgreSQL: localhost:5432
- pgAdmin: http://localhost:5050 (admin@admin.com / admin)

---

### Opción 2: Local Development

```bash
# 1. Crear virtual environment
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar PostgreSQL
# Opción A: Usar Docker solo para PostgreSQL
docker run -d \
  --name webex-calling-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=webex_calling_security \
  -p 5432:5432 \
  postgres:15-alpine

# Opción B: Instalar PostgreSQL localmente
# (Seguir instrucciones de instalación para tu OS)

# 4. Copiar y configurar .env
cp .env.example .env
# Editar .env con tus credenciales

# 5. Inicializar base de datos
python scripts/init_db.py

# 6. Correr FastAPI
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📊 Modelos de Base de Datos

### **call_detail_records** (CDRs)
Almacena todos los registros de llamadas de Webex Calling.

Campos principales:
- `call_id`, `correlation_id`, `related_call_id`
- `start_time`, `duration`, `calling_number`, `called_number`
- `call_type` (International, National, Local)
- `queue_name`, `trunk_name`, `location`
- `metadata` (JSONB para datos flexibles)

### **call_journeys**
Reconstrucción del viaje completo de una llamada.

Campos principales:
- `journey_id`, `related_call_id`
- `route` (texto: "SIP-Bogotá → AA → Cola → Ext.203")
- `t_aa`, `t_queue_1`, `t_agent` (tiempos en cada etapa)
- `agente_final`, `resultado` (atendida/abandonada)

### **users**
Usuarios/Extensiones monitoreados.

Campos principales:
- `user_id`, `user_name`, `extension`
- `location`, `department`
- `risk_score`, `anomaly_count`
- `baseline_data` (JSONB con patrones ML)

### **alerts**
Alertas de seguridad generadas.

Campos principales:
- `alert_type` (unusual_international_calls, mass_dialing, etc.)
- `severity` (LOW, MEDIUM, HIGH, CRITICAL)
- `user_id`, `title`, `description`
- `ai_analysis` (explicación de Claude)
- `status` (open, investigating, resolved)

---

## 🔌 API Endpoints

### Health Check

```bash
GET /health
GET /
```

### Alerts

```bash
# Listar alertas
GET /api/v1/alerts?page=1&page_size=50&severity=high

# Obtener alerta específica
GET /api/v1/alerts/{alert_id}

# Crear alerta
POST /api/v1/alerts
{
  "alert_type": "mass_dialing",
  "severity": "critical",
  "title": "Mass dialing detected",
  "user_id": "user123"
}

# Actualizar alerta
PATCH /api/v1/alerts/{alert_id}
{
  "status": "resolved",
  "resolution_notes": "False positive - authorized campaign"
}

# Estadísticas
GET /api/v1/alerts/stats/summary
```

### CDR (Próximamente)

```bash
GET /api/v1/cdr?start_date=2025-01-01&end_date=2025-01-31
GET /api/v1/cdr/{call_id}
POST /api/v1/cdr/ingest  # Trigger manual CDR ingestion
```

### Detection (Próximamente)

```bash
POST /api/v1/detection/analyze
{
  "user_id": "user123",
  "detection_types": ["international_calls", "mass_dialing"]
}
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con coverage
pytest tests/ --cov=src --cov-report=html

# Solo tests unitarios
pytest tests/unit/ -v

# Solo tests de integración
pytest tests/integration/ -v
```

---

## 📖 Documentación API Interactiva

Una vez levantado el servidor, accede a:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Puedes probar todos los endpoints directamente desde el navegador.

---

## 🔧 Variables de Entorno

Ver `.env.example` para la lista completa. Las más importantes:

```bash
# Webex
WEBEX_ACCESS_TOKEN=your_token
WEBEX_ORG_ID=your_org_id

# Claude AI
ANTHROPIC_API_KEY=your_api_key

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=webex_calling_security
DB_USER=postgres
DB_PASSWORD=your_password

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## 📁 Estructura del Proyecto

```
src/
├── api/
│   ├── routes/
│   │   ├── alerts.py        # Endpoints de alertas
│   │   ├── cdr.py           # Endpoints de CDRs (TODO)
│   │   └── detection.py     # Endpoints de detección (TODO)
│   └── schemas.py           # Pydantic schemas
├── models/
│   ├── base.py              # Base models
│   ├── cdr.py               # CDR & CallJourney models
│   ├── user.py              # User model
│   └── alert.py             # Alert model
├── detectors/               # Anomaly detection logic
│   ├── international_calls.py
│   ├── after_hours.py
│   ├── mass_dialing.py
│   └── call_forwarding.py
├── ingestion/               # CDR ingestion (TODO)
├── utils/
│   └── logger.py
├── config.py                # Configuration
├── database.py              # DB connection & session
└── main.py                  # FastAPI app
```

---

## 🔍 Troubleshooting

### PostgreSQL no se conecta

```bash
# Verificar que PostgreSQL esté corriendo
docker ps | grep postgres

# Ver logs
docker logs webex-calling-db

# Conectar manualmente para verificar
psql -h localhost -U postgres -d webex_calling_security
```

### FastAPI no levanta

```bash
# Verificar logs
docker logs webex-calling-api

# Verificar variables de entorno
docker exec webex-calling-api env | grep DB_
```

### Error de migraciones

```bash
# Resetear base de datos (⚠️ CUIDADO: borra todo)
docker-compose down -v
docker-compose up -d postgres
python scripts/init_db.py
```

---

## 🚧 Próximos Pasos

- [ ] Implementar endpoints de CDR
- [ ] Implementar ingestion automática de CDRs desde Webex
- [ ] Integrar detectores con endpoints de API
- [ ] Agregar autenticación JWT
- [ ] Implementar rate limiting
- [ ] Agregar Redis para caché
- [ ] Implementar Celery para tareas asíncronas
- [ ] CI/CD con GitHub Actions

---

## 📝 Licencia

[Tu licencia aquí]

---

## 🤝 Contribución

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request
