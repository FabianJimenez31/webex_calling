# Sistema de Diseño Davivienda para React + shadcn/ui

## 🎨 Paleta de Colores

### Colores Primarios

| Color | Hex | RGB | Uso |
|-------|-----|-----|-----|
| **Rojo Davivienda** | `#E30518` | rgb(227, 5, 24) | Color principal de marca, CTAs, headers |
| **Rojo Hover** | `#D82828` | rgb(216, 40, 40) | Estados hover de botones |
| **Rojo Oscuro** | `#B30414` | rgb(179, 4, 20) | Estados activos/pressed |
| **Naranja Davivienda** | `#FF7900` | rgb(255, 121, 0) | Acentos, iconos, highlights |
| **Amarillo Davivienda** | `#FFB900` | rgb(255, 185, 0) | Acentos secundarios, badges |

### Colores Neutrales

| Color | Hex | RGB | Uso |
|-------|-----|-----|-----|
| **Marrón Corporativo** | `#685848` | rgb(104, 88, 72) | Texto secundario, bordes |
| **Gris Oscuro** | `#2C2C2C` | rgb(44, 44, 44) | Texto principal |
| **Gris Medio** | `#6B7280` | rgb(107, 114, 128) | Texto secundario |
| **Gris Claro** | `#F3F4F6` | rgb(243, 244, 246) | Fondos, cards |
| **Blanco** | `#FFFFFF` | rgb(255, 255, 255) | Fondos principales |

### Colores de Estado

| Estado | Hex | RGB |
|--------|-----|-----|
| **Success** | `#10B981` | rgb(16, 185, 129) |
| **Warning** | `#F59E0B` | rgb(245, 158, 11) |
| **Error** | `#EF4444` | rgb(239, 68, 68) |
| **Info** | `#3B82F6` | rgb(59, 130, 246) |

---

## 🔤 Tipografía

### Fuente Principal: **Roboto** (Google Fonts)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap" rel="stylesheet">
```

### Scale de Tipografía

| Elemento | Tamaño | Weight | Line Height | Uso |
|----------|--------|--------|-------------|-----|
| **H1** | 48px / 3rem | 700 | 1.2 | Títulos principales |
| **H2** | 36px / 2.25rem | 700 | 1.3 | Títulos de sección |
| **H3** | 30px / 1.875rem | 600 | 1.4 | Subtítulos |
| **H4** | 24px / 1.5rem | 600 | 1.5 | Títulos de card |
| **H5** | 20px / 1.25rem | 500 | 1.5 | Títulos pequeños |
| **H6** | 18px / 1.125rem | 500 | 1.5 | Etiquetas destacadas |
| **Body Large** | 18px / 1.125rem | 400 | 1.6 | Texto principal destacado |
| **Body** | 16px / 1rem | 400 | 1.6 | Texto principal |
| **Body Small** | 14px / 0.875rem | 400 | 1.5 | Texto secundario |
| **Caption** | 12px / 0.75rem | 400 | 1.4 | Etiquetas, metadatos |

---

## 🎯 Componentes de Diseño

### Botones

#### Primario (Rojo Davivienda)
```css
background: #E30518;
color: #FFFFFF;
padding: 12px 24px;
border-radius: 8px;
font-weight: 500;
box-shadow: 0 2px 4px rgba(227, 5, 24, 0.2);

&:hover {
  background: #D82828;
  box-shadow: 0 4px 8px rgba(227, 5, 24, 0.3);
}

&:active {
  background: #B30414;
}
```

#### Secundario (Outline)
```css
background: transparent;
color: #E30518;
border: 2px solid #E30518;
padding: 10px 24px;
border-radius: 8px;
font-weight: 500;

&:hover {
  background: rgba(227, 5, 24, 0.05);
}
```

#### Terciario (Ghost)
```css
background: transparent;
color: #2C2C2C;
padding: 12px 24px;
font-weight: 500;

&:hover {
  background: #F3F4F6;
}
```

### Cards

```css
background: #FFFFFF;
border: 1px solid #E5E7EB;
border-radius: 12px;
padding: 24px;
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
transition: all 0.3s ease;

&:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}
```

### Inputs

```css
background: #FFFFFF;
border: 1px solid #D1D5DB;
border-radius: 8px;
padding: 12px 16px;
font-size: 16px;
color: #2C2C2C;

&:focus {
  outline: none;
  border-color: #E30518;
  box-shadow: 0 0 0 3px rgba(227, 5, 24, 0.1);
}

&::placeholder {
  color: #9CA3AF;
}
```

---

## 📐 Espaciado y Layout

### Sistema de Espaciado (8px base)

```css
--spacing-xs: 4px;    /* 0.25rem */
--spacing-sm: 8px;    /* 0.5rem */
--spacing-md: 16px;   /* 1rem */
--spacing-lg: 24px;   /* 1.5rem */
--spacing-xl: 32px;   /* 2rem */
--spacing-2xl: 48px;  /* 3rem */
--spacing-3xl: 64px;  /* 4rem */
```

### Border Radius

```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
--radius-full: 9999px;
```

### Box Shadows

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.1);
```

### Breakpoints Responsive

```css
--breakpoint-sm: 640px;   /* Mobile landscape */
--breakpoint-md: 768px;   /* Tablet */
--breakpoint-lg: 1024px;  /* Desktop */
--breakpoint-xl: 1280px;  /* Large desktop */
--breakpoint-2xl: 1536px; /* Extra large */
```

---

## 🎭 Efectos y Animaciones

### Transiciones

```css
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
```

### Hover Effects

```css
.hover-lift {
  transition: transform var(--transition-base), box-shadow var(--transition-base);
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}
```

---

## 📱 Componentes Específicos de Davivienda

### Header/Navbar

```css
background: #FFFFFF;
border-bottom: 1px solid #E5E7EB;
height: 72px;
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);

/* Logo height: 40px */
/* Nav links: color #2C2C2C, hover #E30518 */
```

### Footer

```css
background: #2C2C2C;
color: #FFFFFF;
padding: 48px 0;

/* Links: color #9CA3AF, hover #FFFFFF */
```

### CTA Sections

```css
background: linear-gradient(135deg, #E30518 0%, #FF7900 100%);
color: #FFFFFF;
padding: 64px 0;
border-radius: 16px;
```

---

## 🖼️ Assets de Marca

### Logo

- **Formato SVG:** Preferido para escalabilidad
- **Formato PNG:** Para casos específicos
- **Espacio mínimo:** 16px alrededor del logo
- **Tamaño mínimo:** 120px de ancho

### Iconografía

- **Estilo:** Outlined, stroke-width: 2px
- **Color primario:** #E30518
- **Color secundario:** #685848
- **Tamaño estándar:** 24px x 24px

---

## 📋 Guía de Uso

### Do's ✅

- Usar el rojo #E30518 para CTAs principales
- Mantener contraste mínimo 4.5:1 en textos
- Usar Roboto en todos los textos
- Aplicar espaciado consistente (múltiplos de 8px)
- Usar border-radius suaves (8-12px)

### Don'ts ❌

- No usar gradientes excesivos
- No mezclar más de 3 colores en un componente
- No usar tipografías diferentes a Roboto
- No ignorar estados hover/active en elementos interactivos
- No usar sombras muy pronunciadas

---

## 🔗 Referencias

- **Brandfetch:** https://brandfetch.com/davivienda.com
- **Google Fonts (Roboto):** https://fonts.google.com/specimen/Roboto
- **Análisis realizado:** Noviembre 2025
