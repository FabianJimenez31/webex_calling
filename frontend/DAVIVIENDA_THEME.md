# Davivienda Theme Documentation

Este proyecto usa el tema oficial de Davivienda basado en su portal web.

## Colores Oficiales

### Colores Primarios (Usados en la interfaz)

| Color | Hex | Nombre | Uso |
|-------|-----|--------|-----|
| Rojo Primario | `#E30519` | Shojo's Blood | Navegación, botones, CTA, estadísticas |
| Negro | `#010101` | Binary Black | Textos, fondos oscuros |
| Gris Claro | `#F5F5F5` | - | Fondos de secciones, divisores |
| Blanco | `#FFFFFF` | - | Fondo principal |

### Colores del Logo (NO usados en UI)

| Color | Hex | Nombre | Uso |
|-------|-----|--------|-----|
| Dorado | `#F39800` | Kin Gold | Solo techo de casita del logo |
| Amarillo | `#FEE000` | Tibetan Yellow | Solo detalles del logo |

## Tipografía

- **Familia**: Davivienda (custom), Manrope (fallback), sans-serif
- **H1**: 56px / line-height 73px / weight 700
- **Color texto**: `#010101` (Binary Black)

## Componentes Disponibles

### Tailwind Classes

```css
.text-davivienda-red-500    /* #E30519 */
.bg-davivienda-red-500      /* Background rojo */
.text-davivienda-gray-900   /* #010101 Binary Black */
.bg-davivienda-gray-100     /* #F5F5F5 Light gray */
```

### Custom Classes

```css
.btn-davivienda-primary     /* Botón rojo primario */
.btn-davivienda-secondary   /* Botón secundario outline */
.btn-davivienda-ghost       /* Botón transparente */
.card-davivienda            /* Tarjeta con hover effect */
.gradient-davivienda        /* Gradiente rojo (sin naranja) */
.header-davivienda          /* Header con border y shadow */
.badge-davivienda           /* Badge rojo */
```

## Componentes React

Ubicados en `src/components/davivienda/`:
- `Header.tsx` - Navegación principal
- `Hero.tsx` - Hero section con gradiente
- `ProductCard.tsx` - Tarjeta de producto
- `Footer.tsx` - Footer con enlaces

## Ver Demo

```tsx
import { DaviviendaPortalExample } from './examples/DaviviendaPortalExample';

// En tu App.tsx o router
<DaviviendaPortalExample />
```

## Referencias

- Portal oficial: https://www.davivienda.com/
- Fuente custom por: Sumotype Foundry (Bogotá, Colombia)
- Diseño: TXT Agencia Transmedia
