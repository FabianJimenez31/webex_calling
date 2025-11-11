# Webex Calling Security AI - Funcionalidades Implementadas

## Resumen

Sistema completo de seguridad y análisis para Webex Calling con IA, tema Davivienda, y múltiples capacidades de reporting y monitoreo.

**Fecha de implementación**: 2025-11-08

---

## 🎯 Funcionalidades Principales

### 1. ✅ Chat Assistant Conversacional (COMPLETADO)

**Descripción**: Interfaz conversacional en lenguaje natural para consultar datos de llamadas en español e inglés.

**Endpoints**:
- `POST /api/v1/chat/ask` - Hacer preguntas en lenguaje natural
- `GET /api/v1/chat/ask/quick` - Endpoint simplificado con query params
- `GET /api/v1/chat/examples` - Obtener preguntas de ejemplo
- `GET /api/v1/chat/stats` - Estadísticas del sistema

**Características**:
- Análisis de datos de CDRs en tiempo real
- Respuestas estructuradas con métricas clave, insights y recomendaciones
- Soporte para 6 categorías de preguntas:
  - Colas de Llamadas
  - Usuarios y Agentes
  - Análisis Temporal
  - Métricas de Calidad
  - Ubicaciones
  - Infraestructura
- Datos de visualización incluidos en la respuesta

**Ejemplos de preguntas**:
```
¿Cuál es la cola que más llamadas tiene?
¿Cuántas llamadas fallidas hubo hoy?
¿En qué horario hay más llamadas?
¿Qué usuario hizo más llamadas?
```

**Archivo**: `src/services/chat_assistant.py`, `src/api/routes/chat.py`

---

### 2. ✅ Exportación de Reportes PDF/CSV (COMPLETADO)

**Descripción**: Generación y descarga de reportes profesionales en formato PDF y CSV.

**Endpoints**:
- `GET /api/v1/reports/security/pdf` - Reporte PDF de análisis de seguridad
- `GET /api/v1/reports/security/csv` - Reporte CSV de análisis de seguridad
- `GET /api/v1/reports/cdrs/csv` - Exportar CDRs raw a CSV
- `POST /api/v1/reports/chat/pdf` - Generar PDF desde respuesta del chat
- `GET /api/v1/reports/stats` - Estadísticas del sistema de reportes

**Características**:
- **PDF**: Formato profesional con tema Davivienda (colores corporativos)
  - Reportes de seguridad con análisis completo
  - Reportes de chat con pregunta, respuesta y detalles
  - Tablas formateadas y colores según nivel de riesgo

- **CSV**: Exportación de datos para análisis posterior
  - CDRs raw con todos los campos
  - Análisis de seguridad estructurado
  - Compatible con Excel y herramientas de análisis

**Librerías utilizadas**:
- `reportlab` - Generación de PDFs
- `pandas` - Manipulación de datos para CSV

**Archivos**: `src/services/report_generator.py`, `src/api/routes/reports.py`

---

### 3. ✅ Sistema de Alertas Automáticas (COMPLETADO)

**Descripción**: Notificaciones automáticas cuando se detectan anomalías de seguridad (MEDIUM, HIGH, CRITICAL).

**Endpoints**:
- `POST /api/v1/alerts/config/webhooks` - Configurar webhooks (Slack/Teams)
- `POST /api/v1/alerts/config/emails` - Configurar destinatarios de email
- `GET /api/v1/alerts/config/status` - Estado de configuración de alertas
- `GET /api/v1/alerts/history` - Historial de alertas enviadas

**Características**:
- **Webhooks**: Soporte para Slack y Microsoft Teams
  - Formato de mensaje adaptativo según plataforma
  - Colores según nivel de riesgo
  - Información estructurada con anomalías detectadas

- **Email**: Sistema de notificación por correo (requiere configuración SMTP)

- **Alertas automáticas**: Se envían solo para niveles MEDIUM o superior
- **Historial**: Almacenamiento en memoria de las últimas 50 alertas

**Integración**: El sistema de detección (`/api/v1/detection/analyze`) automáticamente envía alertas cuando detecta amenazas.

**Archivos**: `src/services/alert_service.py`, integrado en `src/api/routes/detection.py` y `src/api/routes/alerts.py`

---

### 4. ✅ Análisis Programado (COMPLETADO)

**Descripción**: Sistema de análisis de seguridad automático con programación flexible (horario, diario, personalizado).

**Endpoints**:
- `POST /api/v1/detection/schedule/enable` - Habilitar análisis programado
- `POST /api/v1/detection/schedule/disable/{job_id}` - Deshabilitar tarea programada
- `GET /api/v1/detection/schedule/jobs` - Lista de tareas programadas
- `GET /api/v1/detection/schedule/history` - Historial de análisis programados

**Tipos de programación**:

**1. Horario (Hourly)**:
```json
{
  "schedule_type": "hourly",
  "hours": 1,
  "limit": 100
}
```
Ejecuta análisis cada hora.

**2. Diario (Daily)**:
```json
{
  "schedule_type": "daily",
  "hour": 8,
  "minute": 0,
  "hours": 24,
  "limit": 200
}
```
Ejecuta análisis todos los días a las 08:00 UTC.

**3. Personalizado (Custom)**:
```json
{
  "schedule_type": "custom",
  "interval_minutes": 30,
  "hours": 1,
  "limit": 50
}
```
Ejecuta análisis cada X minutos.

**Características**:
- Análisis automático de CDRs
- Detección de anomalías con IA
- Envío automático de alertas si se detectan amenazas
- Historial de análisis (últimos 100)
- Inicio/parada del scheduler integrado en ciclo de vida de FastAPI

**Librerías utilizadas**:
- `apscheduler` - Programación de tareas asíncronas

**Archivos**: `src/services/scheduler.py`, integrado en `src/main.py` y `src/api/routes/detection.py`

---

## 🔧 Funcionalidades Existentes (Ya implementadas anteriormente)

### 5. Autenticación OAuth 2.0 con Webex
- Three-legged OAuth flow
- Persistencia de tokens en archivo
- Auto-refresh de tokens
- Endpoints: `/auth/login`, `/auth/callback`, `/auth/status`

### 6. Obtención de CDRs
- Integración con Webex Calling API
- Endpoint correcto: `analytics.webexapis.com/v1/cdr_feed`
- Rate limiting: 1 llamada por minuto
- Endpoints: `/api/v1/cdrs/`

### 7. Detección de Anomalías con IA
- OpenRouter API con modelo GPT OSS Safeguard 20B
- Análisis de seguridad, fraude y calidad
- Clasificación de riesgo: LOW, MEDIUM, HIGH, CRITICAL
- Endpoints: `/api/v1/detection/analyze`, `/api/v1/detection/analyze/quick`

### 8. Analytics y Dashboard (Backend)
- Endpoints de analíticas
- Estadísticas de llamadas
- Métricas de calidad

---

## 📊 Datos Reales Procesados

**Organización**: ITS INFOCOMUNICACION SAS
**Ubicaciones**: 7 (Colombia, Costa Rica, Guatemala, El Salvador, Denver, etc.)
**Ubicación principal**: PoC Banco Davivienda
**CDRs procesados**: 167+ registros reales
**Cola principal**: NA (108 llamadas, 64.6% del total)

---

## 🎨 Tema Visual

- **Colores Davivienda**:
  - Rojo corporativo: `#E30519`
  - Negro: `#010101`
  - Gris claro: `#F5F5F5`

Aplicado en:
- Frontend (Tailwind CSS custom theme)
- PDFs (reportlab custom styles)
- Alertas (códigos de color)

---

## 🧪 Estado de Pruebas

### ✅ Probado y funcionando:
1. Chat Assistant - Pregunta "¿Cuál es la cola que más llamadas tiene?" respondida exitosamente
2. Análisis de anomalías - 165 CDRs analizados, Riesgo: LOW
3. Obtención de CDRs - 167 registros obtenidos
4. OAuth - Autenticación exitosa y tokens persistidos

### ⏳ Pendiente de prueba:
1. Exportación PDF/CSV
2. Configuración de alertas (webhooks/emails)
3. Análisis programado
4. Dashboard frontend (pendiente de implementar)

---

## 📁 Estructura de Archivos Nuevos

```
src/
├── services/
│   ├── chat_assistant.py          # ✨ Chat conversacional con IA
│   ├── report_generator.py        # ✨ Generación de PDFs y CSVs
│   ├── alert_service.py            # ✨ Sistema de alertas
│   ├── scheduler.py                # ✨ Análisis programado
│   ├── anomaly_detector.py         # (Existente) Detección con IA
│   ├── webex_client.py             # (Existente) Cliente Webex
│   └── webex_oauth.py              # (Existente) OAuth handler
├── api/routes/
│   ├── chat.py                     # ✨ Endpoints de chat
│   ├── reports.py                  # ✨ Endpoints de reportes
│   ├── detection.py                # (Modificado) +Scheduler endpoints
│   ├── alerts.py                   # (Modificado) +Config endpoints
│   └── ...
└── main.py                         # (Modificado) +Scheduler integration
```

---

## 🚀 Cómo Usar

### 1. Chat Assistant

```bash
# Hacer una pregunta
curl -X POST "http://localhost:8000/api/v1/chat/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"¿Cuál es la cola que más llamadas tiene?","hours":24}'
```

### 2. Generar Reporte PDF

```bash
# Reporte de seguridad
curl "http://localhost:8000/api/v1/reports/security/pdf?hours=24" \
  -o security_report.pdf
```

### 3. Configurar Alertas

```bash
# Configurar webhook de Slack
curl -X POST "http://localhost:8000/api/v1/alerts/config/webhooks" \
  -H "Content-Type: application/json" \
  -d '{"webhook_urls":["https://hooks.slack.com/services/YOUR/WEBHOOK/URL"]}'
```

### 4. Programar Análisis

```bash
# Análisis horario
curl -X POST "http://localhost:8000/api/v1/detection/schedule/enable" \
  -H "Content-Type: application/json" \
  -d '{"schedule_type":"hourly","hours":1,"limit":100}'
```

---

## 📦 Dependencias Nuevas Instaladas

```
reportlab==4.4.4         # Generación de PDFs
pandas==2.3.3            # Manipulación de datos
aiosmtplib==4.0.2       # Envío de emails async
apscheduler==3.11.1     # Programación de tareas
```

---

## 🔜 Próximos Pasos

1. **Dashboard Frontend**: Componentes React para visualizar:
   - Resultados del chat assistant
   - Gráficos de anomalías
   - Historial de alertas
   - Estado del scheduler

2. **Integración Completa**: Conectar frontend con todos los nuevos endpoints

3. **Configuración SMTP**: Para envío real de emails

4. **Persistencia en BD**: Migrar historial de alertas y análisis programados a PostgreSQL

---

## 📝 Notas Técnicas

- **Rate Limits**: Webex CDR API tiene límite de 1 llamada/minuto
- **Tiempo de CDRs**: Disponibles 5 minutos después de la llamada, retención 48 horas
- **Python**: Compatible con Python 3.9+
- **Modelo IA**: `openai/gpt-oss-safeguard-20b` vía OpenRouter
- **Base de datos**: Opcional (API funciona sin PostgreSQL)

---

## 🎯 Objetivos Cumplidos

- [x] Chat conversacional para consultas en lenguaje natural
- [x] Exportación de reportes PDF/CSV profesionales
- [x] Sistema de alertas automáticas (Slack/Teams/Email)
- [x] Análisis programado (horario/diario/personalizado)
- [ ] Dashboard visual (pendiente)

---

**Desarrollado con**: Claude Sonnet 4.5
**Organización**: Davivienda
**Proyecto**: Webex Calling Security AI
