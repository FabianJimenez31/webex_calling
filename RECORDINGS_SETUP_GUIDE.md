# Guía de Configuración para Webex Recordings API

## 🎯 Objetivo
Habilitar el acceso al API de Converged Recordings de Webex Calling para capturar y procesar grabaciones automáticamente.

## ❌ Problema Actual
Los scopes OAuth actuales **NO incluyen** permisos para acceder a grabaciones.

**Scopes actuales:**
```
analytics:read_all spark:organizations_read spark:people_read
```

## ✅ Solución

### Paso 1: Actualizar Scopes en Webex Developer Portal

1. Ve a https://developer.webex.com/my-apps
2. Selecciona tu aplicación OAuth existente
3. En la sección **Scopes**, agrega:

   **Opción A - Admin (Recomendado):**
   ```
   spark-admin:recordings_read
   spark-admin:recordings_write
   ```

   **Opción B - Compliance Officer (Máximo acceso):**
   ```
   spark-compliance:recordings_read
   spark-compliance:recordings_write
   ```

4. **Importante**: También mantén los scopes existentes para CDRs:
   ```
   analytics:read_all
   spark:organizations_read
   spark:people_read
   ```

### Paso 2: Actualizar archivo `.env`

Edita el archivo `.env` y actualiza la línea `WEBEX_SCOPES`:

**Para Admin:**
```bash
WEBEX_SCOPES=analytics:read_all spark:organizations_read spark:people_read spark-admin:recordings_read spark-admin:recordings_write
```

**Para Compliance:**
```bash
WEBEX_SCOPES=analytics:read_all spark:organizations_read spark:people_read spark-compliance:recordings_read spark-compliance:recordings_write
```

### Paso 3: Re-autenticar con Webex

Los scopes solo se aplican en el momento de la autorización inicial. Necesitas volver a autenticarte:

```bash
# 1. Elimina los tokens actuales
rm .webex_tokens.json

# 2. Inicia el backend
cd /home/debian/webex/webex_calling
source venv/bin/activate
python -m uvicorn src.main:app --reload --port 8000

# 3. Visita la URL de login en tu navegador
# http://localhost:8000/auth/login (o https://webex.r0bot.ai/auth/login)

# 4. Autoriza la aplicación con los nuevos scopes

# 5. Verifica el estado
curl http://localhost:8000/auth/status
```

### Paso 4: Verificar Acceso al API de Recordings

Usa el siguiente script para verificar que tienes acceso:

```bash
# Verificar que el token tiene los scopes correctos
curl -X GET "https://webexapis.com/v1/convergedRecordings?serviceType=calling&max=10" \
  -H "Authorization: Bearer $(cat .webex_tokens.json | jq -r '.access_token')"
```

**Respuesta esperada:**
- ✅ `200 OK` con lista de grabaciones → **Acceso correcto**
- ❌ `401 Unauthorized` → Token inválido
- ❌ `403 Forbidden` → Falta de scopes o permisos

## 📋 Requisitos Previos de la Organización

Además de los scopes, tu organización Webex debe tener:

1. **Webex Calling habilitado**
2. **Recording provider configurado**:
   - Webex (Cloud Recording)
   - O BroadWorks
3. **Rol de usuario apropiado**:
   - Full Admin
   - O Compliance Officer

### Verificar Recording Provider

1. Inicia sesión en https://admin.webex.com
2. Ve a **Services** → **Calling**
3. Selecciona una **Location**
4. Ve a **Calling Settings** → **Recording**
5. Verifica que esté habilitado y configurado

## 🧪 Testing

Una vez configurado, puedes probar con:

```bash
# Listar grabaciones recientes
curl -X GET "https://webexapis.com/v1/convergedRecordings?serviceType=calling&from=2025-11-01T00:00:00.000Z&max=50" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Obtener detalles de una grabación
curl -X GET "https://webexapis.com/v1/convergedRecordings/{recordingId}" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Obtener metadata extendida
curl -X GET "https://webexapis.com/v1/convergedRecordings/{recordingId}/metadata" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔍 Troubleshooting

### Error: "Insufficient scope"
- Verifica que actualizaste los scopes en Webex Developer Portal
- Re-autentica eliminando `.webex_tokens.json` y volviendo a hacer login

### Error: "Recording provider not enabled"
- Contacta al administrador de Webex
- Habilita recording en admin.webex.com

### Error: "No recordings found"
- Normal si no hay llamadas grabadas recientemente
- Las grabaciones deben ser de llamadas con recording habilitado
- Verifica que haya llamadas en los últimos días con recording activo

### Token expirado
- El sistema auto-refresha tokens automáticamente
- Si falla, elimina `.webex_tokens.json` y re-autentica

## 📚 Documentación de Referencia

- [Converged Recordings API](https://developer.webex.com/docs/api/v1/converged-recordings)
- [Getting Started with Converged Recordings](https://developer.webex.com/blog/getting-started-with-the-converged-recordings-apis-for-webex-calling)
- [Webex Calling Recording Setup](https://help.webex.com/en-us/article/n3ebtmq/Webex-Calling-Call-Recording)

## ✅ Checklist de Implementación

- [ ] Actualizar scopes en Webex Developer Portal
- [ ] Actualizar `.env` con nuevos scopes
- [ ] Eliminar `.webex_tokens.json`
- [ ] Re-autenticar vía `/auth/login`
- [ ] Verificar acceso con `curl` al API de recordings
- [ ] Confirmar que la organización tiene recording habilitado
- [ ] Probar listar grabaciones recientes
- [ ] Validar que se pueden descargar grabaciones
- [ ] Verificar disponibilidad de transcripciones

## 🚀 Próximos Pasos

Una vez que tengas acceso confirmado al API:

1. ✅ Modelo de datos ya creado (`src/models/recording.py`)
2. ⏳ Implementar servicio de recordings (`src/services/webex_recordings.py`)
3. ⏳ Crear endpoints REST (`src/api/routes/recordings.py`)
4. ⏳ Implementar procesamiento automático (download, transcribe, summarize)
5. ⏳ Configurar scheduler para polling automático
