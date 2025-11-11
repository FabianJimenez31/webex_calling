# Webex Integration Setup Guide

Guía paso a paso para configurar la integración con Webex Calling API.

## 📋 Paso 1: Crear la Integración en Webex

### 1.1 Ir al Portal de Desarrolladores
Accede a: https://developer.webex.com/my-apps/new

### 1.2 Seleccionar Tipo
- ✅ **Create an Integration** (NO Bot)

### 1.3 Información Básica
```
Integration Name: Webex Calling Security AI
Description: AI-powered security monitoring and anomaly detection for Webex Calling
Contact Email: tu-email@davivienda.com
Support Link: https://tu-dominio.com/support (opcional)
```

### 1.4 Redirect URIs
Agregar las siguientes URLs (una por línea):
```
http://localhost:8000/auth/callback
http://localhost:3000/auth/callback
https://tu-dominio.com/auth/callback
```

### 1.5 Scopes Requeridos

**⚠️ IMPORTANTE**: Selecciona EXACTAMENTE estos scopes:

#### Analytics & CDRs (OBLIGATORIOS)
- ✅ `spark-admin:calling_cdr_read` - **Call Detail Records**
- ✅ `analytics:read_all` - Estadísticas y métricas

#### Calling Information
- ✅ `spark:calling_read` - Configuración de llamadas
- ✅ `spark-admin:calling_read` - Admin calling settings

#### Organizations & People
- ✅ `spark-admin:organizations_read` - Info de la organización
- ✅ `spark:people_read` - Info de usuarios

#### Identity
- ✅ `spark:all` - Acceso completo (alternativa a los anteriores)

### 1.6 Crear y Guardar Credenciales
1. Click en **"Add Integration"**
2. ⚠️ **GUARDA INMEDIATAMENTE**:
   - **Client ID**: `C1234567...`
   - **Client Secret**: `abc123...` (solo se muestra UNA VEZ)
   - **OAuth Authorization URL**
   - **Access Token URL**

---

## 🔐 Paso 2: Configurar las Credenciales

### 2.1 Copiar archivo de ejemplo
```bash
cd /Users/fabianjimenez/webex-calling-security-ai
cp .env.example .env
```

### 2.2 Editar `.env` con tus credenciales
```bash
# Webex Integration OAuth Configuration
WEBEX_CLIENT_ID=tu_client_id_aquí
WEBEX_CLIENT_SECRET=tu_client_secret_aquí
WEBEX_REDIRECT_URI=http://localhost:8000/auth/callback
WEBEX_SCOPES=spark-admin:calling_cdr_read spark-admin:organizations_read analytics:read_all spark:people_read

# Las siguientes se obtienen automáticamente después del OAuth
WEBEX_ACCESS_TOKEN=
WEBEX_REFRESH_TOKEN=
WEBEX_ORG_ID=

# Claude AI Configuration
ANTHROPIC_API_KEY=tu_anthropic_key_aquí

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=webex_calling_security
DB_USER=postgres
DB_PASSWORD=tu_password_aquí
```

---

## 🚀 Paso 3: Iniciar el Flujo OAuth

### 3.1 Levantar el Backend
```bash
cd backend
uvicorn src.main:app --reload
```

### 3.2 Iniciar Autenticación
Abre tu navegador en:
```
http://localhost:8000/auth/login
```

### 3.3 Flujo de Autorización
1. Serás redirigido a Webex para autorizar
2. Acepta los permisos solicitados
3. Serás redirigido de vuelta a: `http://localhost:8000/auth/callback`
4. El sistema guardará automáticamente el Access Token y Refresh Token

### 3.4 Verificar Conexión
```bash
curl http://localhost:8000/api/v1/webex/status
```

Deberías ver:
```json
{
  "status": "connected",
  "org_id": "Y2lzY29zcGF...",
  "org_name": "Davivienda",
  "token_expires_in": 86400
}
```

---

## 📊 Paso 4: Probar la API de CDRs

### 4.1 Obtener CDRs Recientes
```bash
curl http://localhost:8000/api/v1/cdrs?limit=10
```

### 4.2 Obtener CDRs con Filtros
```bash
# Por fecha
curl "http://localhost:8000/api/v1/cdrs?start_time=2025-01-01&end_time=2025-01-31"

# Por tipo de llamada
curl "http://localhost:8000/api/v1/cdrs?call_type=International"

# Por usuario
curl "http://localhost:8000/api/v1/cdrs?user_email=juan.perez@davivienda.com"
```

### 4.3 Ejecutar Detección de Anomalías
```bash
curl -X POST http://localhost:8000/api/v1/detection/analyze
```

---

## 🔄 Paso 5: Configurar Actualización Automática

### 5.1 Token Refresh (Automático)
El sistema refrescará automáticamente el token cada 12 horas.

### 5.2 Polling de CDRs (Cron Job)
Configura un cron job para obtener CDRs cada hora:
```bash
# Editar crontab
crontab -e

# Agregar línea
0 * * * * curl -X POST http://localhost:8000/api/v1/cdrs/sync
```

### 5.3 Detección en Tiempo Real
```bash
# Activar detección continua cada 5 minutos
*/5 * * * * curl -X POST http://localhost:8000/api/v1/detection/run
```

---

## 🛠️ Troubleshooting

### Error: "Invalid Client"
- Verifica que `WEBEX_CLIENT_ID` y `WEBEX_CLIENT_SECRET` sean correctos
- Asegúrate de que el Redirect URI coincida exactamente

### Error: "Insufficient Permissions"
- Verifica que seleccionaste todos los scopes necesarios
- Puede que necesites permisos de administrador de Webex

### Error: "Token Expired"
- El Access Token expira cada 14 días
- Usa el Refresh Token para obtener uno nuevo:
```bash
curl -X POST http://localhost:8000/auth/refresh
```

### CDRs Vacíos
- Los CDRs pueden tardar hasta 30 minutos en estar disponibles después de una llamada
- Verifica que tu organización tenga Webex Calling habilitado
- Confirma que tienes permisos de admin

---

## 📚 Recursos Adicionales

- [Webex Calling API Documentation](https://developer.webex.com/docs/api/v1/call-history)
- [OAuth 2.0 Integration Guide](https://developer.webex.com/docs/integrations)
- [CDR Schema Reference](https://developer.webex.com/docs/api/v1/call-history/get-detailed-call-history)

---

## ✅ Checklist

Antes de continuar, verifica que tienes:

- [ ] Integración creada en Webex Developer Portal
- [ ] Client ID y Client Secret guardados
- [ ] Archivo `.env` configurado
- [ ] Backend corriendo en localhost:8000
- [ ] OAuth completado exitosamente
- [ ] Primer CDR obtenido correctamente
- [ ] Detección de anomalías funcionando

---

Una vez completado este setup, el sistema estará listo para:
✅ Obtener CDRs de Webex Calling automáticamente
✅ Detectar anomalías con IA
✅ Generar alertas en tiempo real
✅ Visualizar métricas en el dashboard
