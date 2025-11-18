# Módulo de Grabaciones de Webex Calling

## 📋 Descripción General

Sistema completo para capturar, procesar y consolidar grabaciones de llamadas de Webex Calling, incluyendo:
- Audio original
- Metadatos técnicos completos
- Transcripción (Webex o generada por IA)
- Resumen automático con análisis de sentimiento
- Traducción opcional
- Estructura unificada para consultas

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│  Webex Converged Recordings API                             │
│  (Grabaciones de llamadas con metadata)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  Webex Recordings Service (webex_recordings.py)             │
│  • Listar grabaciones                                       │
│  • Obtener detalles y metadata                              │
│  • Descargar audio y transcripciones                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  Recording Processor (recording_processor.py)               │
│  • Orquestar pipeline completo                              │
│  • Generar resúmenes con IA                                 │
│  • Detectar idioma                                          │
│  • Calcular métricas de calidad                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  Database (Recording Model)                                 │
│  • Almacenamiento consolidado                               │
│  • Tracking de estado de procesamiento                      │
│  • Métricas y análisis                                      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Configuración Inicial

### 1. Scopes de OAuth Requeridos

Asegúrate que en tu archivo `.env` tengas:

```bash
WEBEX_SCOPES=analytics:read_all spark:organizations_read spark:people_read spark-admin:calling_cdr_read spark-admin:recordings_read spark-admin:recordings_write
```

**Crítico**: Los siguientes scopes son obligatorios:
- `spark-admin:calling_cdr_read` - Para CDRs con números completos
- `spark-admin:recordings_read` - Para leer grabaciones
- `spark-admin:recordings_write` - Para eliminar grabaciones (opcional)

### 2. Re-autenticar con Nuevos Scopes

Si actualizaste los scopes, necesitas re-autenticar:

```bash
cd /home/debian/webex/webex_calling

# Eliminar tokens antiguos
rm .webex_tokens.json

# Iniciar backend
source venv/bin/activate
python -m uvicorn src.main:app --reload --port 8000

# Visitar en navegador
https://webex.r0bot.ai/auth/login
```

### 3. Verificar Acceso

```bash
# Usando el script de verificación
python3 scripts/verify_recordings_access.py

# O usar el endpoint de test
curl http://localhost:8000/api/v1/recordings/test/webex-access
```

## 📡 API Endpoints

### 1. Listar Grabaciones

```bash
GET /api/v1/recordings/

Query Parameters:
- skip: int (default: 0) - Paginación
- limit: int (default: 50, max: 500) - Resultados por página
- status: string - Filtrar por estado (pending, completed, failed, etc.)
- from_date: ISO datetime - Desde fecha
- to_date: ISO datetime - Hasta fecha

Ejemplo:
curl "http://localhost:8000/api/v1/recordings/?limit=10&status=completed"
```

**Respuesta:**
```json
{
  "total": 10,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "recordingId": "abc123...",
      "timestamp": "2025-11-13T10:30:00Z",
      "caller": "user@example.com",
      "callee": "+1234567890",
      "duration": 180.5,
      "transcript_text": "Hola, buenos días...",
      "summary_text": "Cliente solicita información sobre...",
      "processing_status": "completed",
      "quality_score": 1.0
    }
  ]
}
```

### 2. Obtener Detalles de Una Grabación

```bash
GET /api/v1/recordings/{recording_id}

Ejemplo:
curl "http://localhost:8000/api/v1/recordings/abc123..."
```

### 3. Procesar Nuevas Grabaciones

```bash
POST /api/v1/recordings/fetch

Query Parameters:
- hours: int (default: 24, max: 168) - Cuántas horas atrás buscar
- limit: int (default: 100, max: 1000) - Máximo a procesar

Ejemplo:
curl -X POST "http://localhost:8000/api/v1/recordings/fetch?hours=24&limit=50"
```

**Este endpoint:**
1. Consulta Webex por grabaciones nuevas
2. Descarga audio y transcripciones
3. Genera resúmenes con IA
4. Detecta idioma
5. Guarda en base de datos

**Respuesta:**
```json
{
  "success": true,
  "processed_count": 5,
  "recordings": [...]
}
```

### 4. Reprocesar una Grabación

```bash
POST /api/v1/recordings/{recording_id}/reprocess

Ejemplo:
curl -X POST "http://localhost:8000/api/v1/recordings/abc123.../reprocess"
```

Útil si el procesamiento falló o quieres regenerar resúmenes.

### 5. Eliminar una Grabación

```bash
DELETE /api/v1/recordings/{recording_id}?delete_from_webex=false

Query Parameters:
- delete_from_webex: bool (default: false) - También borrar de Webex

Ejemplo:
# Solo marca como eliminada en DB (soft delete)
curl -X DELETE "http://localhost:8000/api/v1/recordings/abc123..."

# También elimina de Webex
curl -X DELETE "http://localhost:8000/api/v1/recordings/abc123...?delete_from_webex=true"
```

### 6. Estadísticas

```bash
GET /api/v1/recordings/stats/summary

Ejemplo:
curl "http://localhost:8000/api/v1/recordings/stats/summary"
```

**Respuesta:**
```json
{
  "total_recordings": 150,
  "by_status": {
    "pending": 5,
    "completed": 140,
    "failed": 3,
    "partial": 2
  },
  "with_transcripts": 135,
  "with_summaries": 140,
  "average_quality_score": 0.95,
  "total_storage_mb": 1024.5
}
```

### 7. Descargar Audio

```bash
GET /api/v1/recordings/download/{recording_id}/audio

Ejemplo:
curl "http://localhost:8000/api/v1/recordings/download/abc123.../audio"
```

## 🔄 Pipeline de Procesamiento

Cada grabación pasa por estos pasos:

### Paso 1: Fetch Details
- Obtiene información completa de Webex
- Extrae participantes, duración, timestamps

### Paso 2: Fetch Metadata
- Obtiene metadata extendida (si disponible)
- Información de red, flujo de llamada, privacy flags

### Paso 3: Download Audio
- Descarga archivo de audio desde Webex
- Guarda en: `data/recordings/YYYY/MM/DD/{recording_id}.mp3`
- Registra tamaño y formato

### Paso 4: Download/Generate Transcript
- **Si Webex provee transcripción**: Descarga VTT y extrae texto
- **Si NO hay transcripción**: Marca para procesamiento externo (Whisper, Google STT, etc.)

### Paso 5: Generate Summary
- Usa OpenRouter AI para generar:
  - Resumen conciso (2-3 oraciones)
  - Puntos clave (bullet points)
  - Tópicos discutidos
  - Action items
  - Análisis de sentimiento

### Paso 6: Detect Language
- Detecta idioma del transcript
- Calcula confianza de detección

### Resultado
- Estado: `completed` (éxito total), `partial` (parcial), `failed` (falló)
- Quality score: 0.0 a 1.0 (porcentaje de pasos completados)
- Errores: Lista de errores si hubo problemas

## 📊 Modelo de Datos

### Campos Principales

```python
Recording:
    # Identificación
    recording_id: str (único)
    timestamp: datetime

    # Participantes
    caller: str
    callee: str
    caller_name: str
    callee_name: str

    # Audio
    audio_url: str (Webex URL)
    audio_local_path: str (ruta local)
    audio_format: str (mp3, wav, etc.)
    audio_size_bytes: int

    # Transcripción
    transcript_text: str (texto final)
    transcript_vtt_path: str (archivo VTT)
    transcript_source: str (webex, whisper, etc.)
    has_webex_transcript: bool

    # Resumen
    summary_text: str
    summary_bullet_points: json
    key_topics: json
    action_items: json
    summary_source: str

    # Análisis
    sentiment_score: float (-1.0 a 1.0)
    sentiment_label: str (positive, neutral, negative)
    detected_language: str (es, en, etc.)

    # Procesamiento
    processing_status: enum (pending, completed, failed, partial)
    processing_steps_completed: json
    processing_errors: json
    quality_score: float (0.0 a 1.0)

    # Metadata
    webex_metadata: json
    participants: json
    duration: float
```

## 🔧 Uso Programático

### Desde Python

```python
from src.services.webex_recordings import webex_recordings_service
from src.services.recording_processor import recording_processor
from src.database import get_async_db

# Listar grabaciones de Webex
recordings = await webex_recordings_service.list_recordings(
    service_type="calling",
    from_date=datetime.utcnow() - timedelta(days=7),
    max_results=50
)

# Procesar grabaciones nuevas
async with get_async_db() as db:
    processed = await recording_processor.fetch_and_process_new_recordings(
        db=db,
        hours=24,
        limit=100
    )
```

## ⚙️ Configuración Avanzada

### Almacenamiento de Archivos

Los archivos se guardan en:
```
data/
├── recordings/
│   └── YYYY/MM/DD/
│       └── {recording_id}.mp3
└── transcripts/
    └── YYYY/MM/DD/
        └── {recording_id}.vtt
```

### Personalizar Resúmenes

Edita el prompt en `recording_processor.py` método `_generate_summary()`:

```python
prompt = f"""Analyze this call recording transcript and provide:
1. A concise summary in Spanish
2. ...
"""
```

### Añadir Servicios de Transcripción Externa

Para integrar Whisper, Google STT, etc., modifica `recording_processor.py`:

```python
# En el paso de transcripción
if not recording.has_webex_transcript:
    # Llamar a tu servicio externo
    transcript = await whisper_service.transcribe(recording.audio_local_path)
    recording.transcript_text = transcript
    recording.transcript_source = "whisper"
```

## 📈 Casos de Uso

### 1. Monitoreo de Calidad de Llamadas

```bash
# Obtener grabaciones con sentimiento negativo
curl "http://localhost:8000/api/v1/recordings/?limit=100" | \
  jq '.items[] | select(.sentiment.label == "negative")'
```

### 2. Análisis de Tópicos

```bash
# Ver tópicos más discutidos
curl "http://localhost:8000/api/v1/recordings/" | \
  jq '.items[].key_topics' | sort | uniq -c
```

### 3. Auditoría y Cumplimiento

```bash
# Descargar todas las grabaciones de un período
for id in $(curl "http://localhost:8000/api/v1/recordings/?from_date=2025-11-01" | jq -r '.items[].recordingId'); do
  curl "http://localhost:8000/api/v1/recordings/download/$id/audio" -o "$id.mp3"
done
```

### 4. Procesamiento Automático Programado

Usa el scheduler para procesar automáticamente:

```python
# En scheduler.py, agregar job
scheduler.add_job(
    func=fetch_and_process_recordings,
    trigger="interval",
    hours=1,  # Cada hora
    id="recordings_processor"
)
```

## 🐛 Troubleshooting

### No se encuentran grabaciones

**Problema**: `GET /recordings` retorna lista vacía

**Soluciones**:
1. Ejecutar primero: `POST /recordings/fetch` para traer de Webex
2. Verificar que hay grabaciones en Webex en el rango de fechas
3. Confirmar que las llamadas tenían recording habilitado

### Error 403 al acceder al API

**Problema**: "Missing required scopes"

**Solución**:
1. Verificar scopes en `.env`
2. Re-autenticar eliminando `.webex_tokens.json`
3. Confirmar en Webex Developer Portal que la app tiene los scopes

### Procesamiento se queda en "pending"

**Problema**: Recording con status `pending` sin avanzar

**Soluciones**:
1. Revisar logs del backend para errores
2. Intentar reprocesar: `POST /recordings/{id}/reprocess`
3. Verificar que OpenRouter API key es válida

### No hay transcripciones

**Problema**: `transcript_text` es null

**Explicación**: Webex no siempre provee transcripciones automáticamente

**Soluciones**:
1. Habilitar transcripción automática en Webex admin
2. Implementar servicio STT externo (Whisper, Google, etc.)
3. Las transcripciones pueden tomar tiempo en generarse en Webex

## 📚 Referencias

- **Webex Converged Recordings API**: https://developer.webex.com/docs/api/v1/converged-recordings
- **Getting Started Guide**: https://developer.webex.com/blog/getting-started-with-the-converged-recordings-apis-for-webex-calling
- **OAuth Scopes**: https://developer.webex.com/docs/integrations

## ✅ Checklist de Implementación

- [x] Modelo de datos (Recording)
- [x] Servicio de integración Webex (webex_recordings.py)
- [x] Procesador de pipeline (recording_processor.py)
- [x] Endpoints REST (/api/v1/recordings/*)
- [x] Scopes OAuth configurados
- [ ] Re-autenticación completada
- [ ] Test de acceso exitoso
- [ ] Primera ejecución de `/fetch`
- [ ] Verificar grabaciones en DB
- [ ] Configurar procesamiento automático (scheduler)
- [ ] Implementar STT externo (opcional)
- [ ] Implementar traducción (opcional)

## 🎯 Próximos Pasos

1. **Completar re-autenticación** con los nuevos scopes
2. **Ejecutar primer fetch**: `POST /api/v1/recordings/fetch?hours=168&limit=50`
3. **Verificar resultados**: `GET /api/v1/recordings/stats/summary`
4. **Configurar scheduler** para procesamiento automático cada hora
5. **Integrar con frontend** (dashboard de grabaciones)
6. **Implementar servicios avanzados**:
   - Whisper para STT
   - DeepL para traducción
   - Análisis de keywords personalizados
