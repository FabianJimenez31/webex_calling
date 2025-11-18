# Problema de Acceso a Webex Converged Recordings API

## 🔴 Estado Actual: BLOQUEADO

### Usuario Autenticado
- **Nombre**: Fabian Jimenez
- **Email**: fabian@brainerhq.com
- **Extensión**: 1998
- **Organización**: ITS INFOCOMUNICACION SAS
- **User ID**: Y2lzY29zcGFyazovL3VzL1BFT1BMRS8zNzk5NzQ4OS00M2E4LTQ4ZmUtOGUyMS1hMzU0NTdkODc3MDg

### Scopes OAuth Configurados ✅
```
✓ spark-admin:calling_cdr_read
✓ spark-admin:recordings_read
✓ spark-admin:recordings_write
✓ analytics:read_all
✓ spark:people_read
✓ spark:organizations_read
```

### Token Status ✅
- **Estado**: Válido
- **Expira**: 2025-11-27 12:56:46 (14 días)
- **Tipo**: Bearer
- **Refresh token**: Disponible

## ❌ Error Encontrado

### Request
```bash
GET https://webexapis.com/v1/convergedRecordings?serviceType=calling&max=5
Authorization: Bearer [token_válido]
```

### Response
```json
{
  "message": "The server understood the request, but refused to fulfill it because the access token is missing required scopes or the user is missing required roles or licenses.",
  "trackingId": "ROUTERGW_096b5828-7ee3-4f9e-8828-5ed8d4465776"
}
```

**Status Code**: 403 Forbidden

## 🔍 Análisis del Problema

El mensaje de error tiene dos partes:
1. ~~"missing required scopes"~~ ← **NO ES ESTO** (los scopes están correctos)
2. **"user is missing required roles or licenses"** ← **ESTE ES EL PROBLEMA**

### Causa Raíz
Aunque la aplicación OAuth tiene los scopes correctos (`spark-admin:recordings_read`), el **usuario de Webex** (Fabian Jimenez) **NO tiene el rol de administrador necesario** en la organización para acceder al API de Converged Recordings.

### Roles Requeridos

Según la documentación de Webex, para acceder al API de Converged Recordings se necesita **uno de estos roles**:

#### Opción 1: Full Administrator
- Rol: `Full Administrator`
- Permisos: Acceso completo a todas las funciones de administración
- API Access: ✅ Converged Recordings

#### Opción 2: Compliance Officer
- Rol: `Compliance Officer`
- Permisos: Acceso a grabaciones y compliance
- API Access: ✅ Converged Recordings
- Scopes requeridos: `spark-compliance:recordings_read`

#### Opción 3: User & Device Administrator (limitado)
- Rol: `User and Device Administrator`
- Permisos: Gestión de usuarios y dispositivos
- API Access: ⚠️ Limitado (solo sus propias grabaciones)

### Tu Usuario Actual
El usuario `fabian@brainerhq.com` parece ser un **usuario regular** sin roles administrativos, por eso el API rechaza las peticiones.

## ✅ Soluciones

### Solución 1: Asignar Rol de Full Administrator (Recomendado)

**Quién lo hace**: Administrador principal de la organización Webex

**Pasos**:
1. Iniciar sesión en **Control Hub**: https://admin.webex.com
2. Ir a **Users** → Buscar `fabian@brainerhq.com`
3. Click en el usuario → **Roles and Security**
4. Agregar rol: **Full Administrator**
5. Guardar cambios
6. Esperar 5-10 minutos para que se propague
7. **NO es necesario re-autenticar**, el token actual funcionará

### Solución 2: Asignar Rol de Compliance Officer

**Pasos**:
1. Iniciar sesión en **Control Hub**: https://admin.webex.com
2. Ir a **Users** → Buscar `fabian@brainerhq.com`
3. Click en el usuario → **Roles and Security**
4. Agregar rol: **Compliance Officer**
5. Guardar cambios
6. **Actualizar scopes en la app OAuth**:
   - Cambiar de `spark-admin:recordings_read`
   - A `spark-compliance:recordings_read`
7. Re-autenticar la aplicación

### Solución 3: Usar Cuenta de Administrador Existente

Si hay otro usuario en la organización que ya tiene rol de administrador:

1. Cerrar sesión actual
2. Re-autenticar con cuenta de administrador
3. Los tokens se actualizarán automáticamente

## 🧪 Verificación Post-Solución

Una vez que se asigne el rol administrativo:

### Paso 1: Esperar propagación (5-10 minutos)

### Paso 2: Verificar acceso
```bash
cd /home/debian/webex/webex_calling
source venv/bin/activate
python3 scripts/verify_recordings_access.py
```

**Resultado esperado**: ✅ SUCCESS

### Paso 3: Probar endpoint
```bash
curl "http://localhost:8000/api/v1/recordings/test/webex-access"
```

**Resultado esperado**:
```json
{
  "status": "success",
  "has_access": true,
  "recordings_count": N,
  "message": "Successfully accessed Webex Recordings API"
}
```

### Paso 4: Procesar grabaciones
```bash
curl -X POST "http://localhost:8000/api/v1/recordings/fetch?hours=168&limit=50"
```

## 📋 Checklist de Requisitos

Para que el módulo de recordings funcione, necesitas:

- [x] Scopes OAuth correctos en la aplicación
- [x] Token válido con scopes activos
- [ ] **Usuario con rol de Full Administrator o Compliance Officer** ← FALTA
- [ ] Organización con Webex Calling Recording habilitado
- [ ] Licencias de Webex Calling activas
- [ ] Recording provider configurado (Webex o BroadWorks)

## 🎯 Próximos Pasos

1. **Contactar al administrador principal** de ITS INFOCOMUNICACION SAS
2. **Solicitar rol de Full Administrator** para `fabian@brainerhq.com`
3. **Esperar 5-10 minutos** después de la asignación
4. **Ejecutar**: `python3 scripts/verify_recordings_access.py`
5. **Si es exitoso**: `curl -X POST "http://localhost:8000/api/v1/recordings/fetch?hours=24"`

## 📞 Soporte

Si después de asignar el rol administrativo aún tienes problemas:

1. Verificar que la organización tiene Webex Calling Recording habilitado
2. Verificar que hay licencias de Professional o superior
3. Contactar a Cisco TAC con el tracking ID del error
4. Revisar logs en Control Hub → Troubleshooting → Logs

## 📚 Referencias

- **Webex Admin Roles**: https://help.webex.com/en-us/article/n5b8hls/Assign-Organization-Account-Roles-in-Control-Hub
- **Converged Recordings API**: https://developer.webex.com/docs/api/v1/converged-recordings
- **Compliance API**: https://developer.webex.com/docs/compliance

---

**Estado**: Esperando asignación de rol administrativo para el usuario `fabian@brainerhq.com`

**Fecha**: 2025-11-13
