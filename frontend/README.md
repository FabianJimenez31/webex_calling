# Webex Calling Security AI - Frontend

Dashboard de seguridad y detección de anomalías para Webex Calling con análisis de inteligencia artificial.

## 🚀 Stack Tecnológico

- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite 7
- **Estilos**: Tailwind CSS 3.4
- **Componentes**: shadcn/ui
- **Tema**: Davivienda (Colores oficiales: #E30519, #010101, #F5F5F5)
- **Fuente**: Davivienda (custom), Manrope (fallback)

## 📂 Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/
│   │   ├── davivienda/          # Componentes del tema Davivienda
│   │   │   ├── Header.tsx
│   │   │   ├── Hero.tsx
│   │   │   ├── ProductCard.tsx
│   │   │   └── Footer.tsx
│   │   └── ui/                  # Componentes shadcn/ui
│   ├── examples/
│   │   └── DaviviendaPortalExample.tsx  # Demo del tema
│   ├── lib/
│   │   └── utils.ts             # Utilidades (cn helper)
│   ├── App.tsx                  # Dashboard principal
│   ├── index.css               # Estilos globales + Davivienda theme
│   └── main.tsx
├── tailwind.config.js          # Configuración de Tailwind con colores Davivienda
├── DAVIVIENDA_THEME.md         # Documentación del tema
└── README.md
```

## 🎨 Tema Davivienda

El proyecto usa los colores oficiales del portal de Davivienda:

- **Rojo Primario**: `#E30519` (Shojo's Blood) - Botones, alertas, CTA
- **Negro**: `#010101` (Binary Black) - Textos
- **Gris Claro**: `#F5F5F5` - Fondos de secciones
- **Blanco**: `#FFFFFF` - Fondo principal

Ver [DAVIVIENDA_THEME.md](./DAVIVIENDA_THEME.md) para más detalles.

## 🛠️ Desarrollo

### Instalar dependencias
```bash
npm install
```

### Iniciar servidor de desarrollo
```bash
npm run dev
```

Abre [http://localhost:5173](http://localhost:5173) en tu navegador.

### Build para producción
```bash
npm run build
```

### Preview del build
```bash
npm run preview
```

## 📊 Características del Dashboard

### Métricas Principales
- **Alertas Activas**: Número de amenazas detectadas sin resolver
- **Llamadas Analizadas**: Total de llamadas procesadas por el sistema
- **Amenazas Bloqueadas**: Incidentes de seguridad prevenidos
- **Precisión AI**: Accuracy del modelo de detección de anomalías

### Tipos de Alertas Detectadas

1. **Llamadas Internacionales Inusuales** (Alta)
   - Detección de llamadas a países no habituales
   - Identificación de números no registrados

2. **Actividad Fuera de Horario** (Media)
   - Llamadas en horarios inusuales
   - Patrones de uso fuera de lo normal

3. **Patrón de Marcación Masiva** (Media)
   - Múltiples llamadas en corto período
   - Posible campaña de spam o phishing

4. **Desvío de Llamadas Sospechoso** (Alta)
   - Cambios no autorizados en configuración
   - Desvíos a números externos

## 🔗 Integración con Backend

El frontend se conectará a la API FastAPI en:
- Desarrollo: `http://localhost:8000`
- Producción: `TBD`

### Endpoints principales:
- `GET /api/v1/alerts` - Lista de alertas
- `GET /api/v1/stats` - Métricas del dashboard
- `POST /api/v1/alerts` - Crear nueva alerta
- `PUT /api/v1/alerts/:id` - Actualizar estado de alerta

## 🎯 Próximos Pasos

- [ ] Conectar con API del backend
- [ ] Implementar autenticación
- [ ] Agregar gráficas con Chart.js/Recharts
- [ ] Implementar filtros y búsqueda
- [ ] Página de detalles de alertas
- [ ] Sistema de notificaciones en tiempo real
- [ ] Modo oscuro (dark mode)
- [ ] Dashboard de reportes

## 📝 Notas

- El tema Davivienda está guardado en `src/examples/DaviviendaPortalExample.tsx`
- Los componentes usan las clases de Tailwind configuradas con los colores oficiales
- El proyecto sigue las convenciones de shadcn/ui para componentes reutilizables
