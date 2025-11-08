# 🚀 Guía de Implementación - Tema Davivienda con React + shadcn/ui

## 📋 Tabla de Contenidos

1. [Configuración Inicial](#configuración-inicial)
2. [Instalación de Dependencias](#instalación-de-dependencias)
3. [Configuración de Tailwind](#configuración-de-tailwind)
4. [Configuración de shadcn/ui](#configuración-de-shadcnui)
5. [Uso de Componentes](#uso-de-componentes)
6. [Ejemplos Prácticos](#ejemplos-prácticos)

---

## 1. Configuración Inicial

### Crear proyecto React con Vite

```bash
# Con Vite (recomendado)
npm create vite@latest my-davivienda-app -- --template react-ts
cd my-davivienda-app

# O con Next.js
npx create-next-app@latest my-davivienda-app --typescript --tailwind
cd my-davivienda-app
```

---

## 2. Instalación de Dependencias

```bash
# Dependencias principales
npm install tailwindcss postcss autoprefixer
npm install class-variance-authority clsx tailwind-merge
npm install lucide-react # Para iconos

# shadcn/ui CLI
npx shadcn-ui@latest init
```

Durante la inicialización de shadcn/ui, selecciona:
- **Style:** Default
- **Base color:** Slate
- **CSS variables:** Yes

---

## 3. Configuración de Tailwind

### 3.1. Reemplazar `tailwind.config.js`

Copia el contenido de `tailwind.config.davivienda.js` a tu `tailwind.config.js`:

```bash
# En tu proyecto
cp tailwind.config.davivienda.js tailwind.config.js
```

### 3.2. Actualizar estilos globales

Reemplaza el contenido de `src/index.css` (o `app/globals.css` en Next.js) con el contenido de `globals.davivienda.css`:

```bash
cp globals.davivienda.css src/index.css
# O para Next.js:
# cp globals.davivienda.css app/globals.css
```

---

## 4. Configuración de shadcn/ui

### 4.1. Instalar componentes base

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add label
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add navigation-menu
```

### 4.2. Estructura de carpetas

```
src/
├── components/
│   ├── ui/              # Componentes de shadcn/ui
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── davivienda/      # Componentes personalizados de Davivienda
│   │   ├── header.tsx
│   │   ├── hero.tsx
│   │   ├── product-card.tsx
│   │   └── footer.tsx
├── lib/
│   └── utils.ts         # Utilidades (cn helper)
├── App.tsx
└── index.css
```

---

## 5. Uso de Componentes

### 5.1. Botones Davivienda

```tsx
import React from 'react';

function MyComponent() {
  return (
    <div className="space-y-4">
      {/* Botón Primario */}
      <button className="btn-davivienda-primary">
        Abrir Cuenta
      </button>

      {/* Botón Secundario */}
      <button className="btn-davivienda-secondary">
        Conocer Más
      </button>

      {/* Botón Ghost */}
      <button className="btn-davivienda-ghost">
        Ingresar
      </button>

      {/* Botón Orange */}
      <button className="btn-davivienda-orange">
        Acción Especial
      </button>
    </div>
  );
}
```

### 5.2. Cards

```tsx
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

function ProductCard() {
  return (
    <Card className="card-davivienda hover-lift">
      <CardHeader>
        <CardTitle>Cuenta de Ahorros</CardTitle>
        <CardDescription>
          Abre tu cuenta 100% digital
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p>Beneficios y características aquí</p>
      </CardContent>
      <CardFooter>
        <button className="link-davivienda">
          Ver más →
        </button>
      </CardFooter>
    </Card>
  );
}
```

### 5.3. Formularios

```tsx
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

function ContactForm() {
  return (
    <form className="space-y-4">
      <div>
        <Label htmlFor="name">Nombre Completo</Label>
        <Input
          id="name"
          type="text"
          placeholder="Juan Pérez"
          className="input-davivienda"
        />
      </div>

      <div>
        <Label htmlFor="email">Correo Electrónico</Label>
        <Input
          id="email"
          type="email"
          placeholder="tu@email.com"
          className="input-davivienda"
        />
      </div>

      <button type="submit" className="btn-davivienda-primary w-full">
        Enviar
      </button>
    </form>
  );
}
```

### 5.4. Gradientes y CTA

```tsx
function CTASection() {
  return (
    <section className="gradient-davivienda my-12 p-12 rounded-2xl">
      <div className="max-w-2xl mx-auto text-center text-white">
        <h2 className="text-h2 mb-4">
          ¿Listo para comenzar?
        </h2>
        <p className="text-body-lg mb-8 opacity-90">
          Abre tu cuenta en minutos y disfruta de todos los beneficios
        </p>
        <button className="bg-white text-davivienda-red-500 px-8 py-4 rounded-lg font-semibold hover:bg-gray-50">
          Abrir Cuenta Ahora
        </button>
      </div>
    </section>
  );
}
```

---

## 6. Ejemplos Prácticos

### Página de Inicio Completa

Ver el archivo `components-davivienda-examples.tsx` para una implementación completa que incluye:

- ✅ Header con navegación
- ✅ Hero section con gradiente
- ✅ Grid de productos con cards
- ✅ Sección de estadísticas
- ✅ Formulario de contacto
- ✅ Footer completo

### Importar y usar:

```tsx
// App.tsx
import DaviviendaExamplePage from './components-davivienda-examples';

function App() {
  return <DaviviendaExamplePage />;
}

export default App;
```

---

## 7. Paleta de Colores en Código

### Uso directo de colores Davivienda

```tsx
// Colores principales
<div className="bg-davivienda-red-500 text-white">
  Fondo rojo Davivienda
</div>

<div className="bg-davivienda-orange-500 text-white">
  Fondo naranja Davivienda
</div>

<div className="bg-davivienda-yellow-500 text-davivienda-yellow-900">
  Fondo amarillo Davivienda
</div>

<div className="bg-davivienda-brown-500 text-white">
  Fondo marrón corporativo
</div>

// Variantes
<button className="bg-davivienda-red-500 hover:bg-davivienda-red-600 active:bg-davivienda-red-700">
  Botón con estados
</button>
```

---

## 8. Tipografía

### Headings

```tsx
<h1 className="text-h1">Título Principal</h1>
<h2 className="text-h2">Título Secundario</h2>
<h3 className="text-h3">Subtítulo</h3>
<h4 className="text-h4">Título de Card</h4>
<h5 className="text-h5">Título Pequeño</h5>
<h6 className="text-h6">Etiqueta</h6>
```

### Body Text

```tsx
<p className="text-body-lg">Texto principal destacado</p>
<p className="text-body">Texto principal</p>
<p className="text-body-sm">Texto secundario</p>
<p className="text-caption">Caption o metadata</p>
```

---

## 9. Utilidades Personalizadas

### Espaciado

```tsx
<div className="spacing-md">  {/* gap: 16px */}
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<div className="spacing-lg">  {/* gap: 24px */}
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

### Hover Lift Effect

```tsx
<div className="hover-lift">
  {/* Este elemento se elevará al hacer hover */}
  <img src="/product.jpg" alt="Product" />
</div>
```

### Links

```tsx
<a href="#" className="link-davivienda">
  Click aquí
</a>
```

### Badges

```tsx
<span className="badge-davivienda">
  Nuevo
</span>
```

---

## 10. Modo Oscuro (Dark Mode)

### Activar modo oscuro

```tsx
// En tu componente raíz
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    // Activar dark mode
    document.documentElement.classList.add('dark');

    // O desactivar
    // document.documentElement.classList.remove('dark');
  }, []);

  return (
    <div className="min-h-screen">
      {/* Tu contenido */}
    </div>
  );
}
```

### Toggle de dark mode

```tsx
import { useState } from 'react';

function DarkModeToggle() {
  const [isDark, setIsDark] = useState(false);

  const toggleDarkMode = () => {
    if (isDark) {
      document.documentElement.classList.remove('dark');
    } else {
      document.documentElement.classList.add('dark');
    }
    setIsDark(!isDark);
  };

  return (
    <button
      onClick={toggleDarkMode}
      className="btn-davivienda-ghost"
    >
      {isDark ? '☀️' : '🌙'}
    </button>
  );
}
```

---

## 11. Responsive Design

### Breakpoints

```tsx
// Mobile first approach
<div className="
  grid
  grid-cols-1           /* Mobile: 1 columna */
  md:grid-cols-2        /* Tablet: 2 columnas */
  lg:grid-cols-3        /* Desktop: 3 columnas */
  xl:grid-cols-4        /* Large: 4 columnas */
">
  {/* Cards */}
</div>

// Spacing responsive
<div className="
  p-4                   /* Mobile: 16px padding */
  md:p-6                /* Tablet: 24px padding */
  lg:p-8                /* Desktop: 32px padding */
">
  {/* Contenido */}
</div>
```

---

## 12. Optimización de Fuentes

### Agregar Roboto en `index.html`

```html
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />

    <!-- Google Fonts - Roboto -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap" rel="stylesheet">

    <title>Davivienda</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

---

## 13. Checklist de Implementación

- [ ] ✅ Proyecto React/Next.js creado
- [ ] ✅ Tailwind CSS instalado y configurado
- [ ] ✅ `tailwind.config.davivienda.js` copiado
- [ ] ✅ `globals.davivienda.css` aplicado
- [ ] ✅ shadcn/ui inicializado
- [ ] ✅ Componentes base instalados (button, card, input, etc.)
- [ ] ✅ Fuente Roboto agregada
- [ ] ✅ Estructura de carpetas creada
- [ ] ✅ Componentes de ejemplo implementados
- [ ] ✅ Responsive design verificado
- [ ] ✅ Dark mode (opcional) configurado

---

## 14. Recursos Adicionales

### Archivos de Referencia

- `DAVIVIENDA_DESIGN_SYSTEM.md` - Sistema de diseño completo
- `tailwind.config.davivienda.js` - Configuración de Tailwind
- `globals.davivienda.css` - Estilos globales y clases custom
- `components-davivienda-examples.tsx` - Componentes de ejemplo

### Documentación Externa

- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/) - Base de shadcn/ui
- [Google Fonts - Roboto](https://fonts.google.com/specimen/Roboto)

---

## 15. Soporte y Contribuciones

Si encuentras algún problema o tienes sugerencias, por favor:

1. Revisa la documentación del sistema de diseño
2. Verifica que los colores y estilos coincidan con la guía
3. Consulta los ejemplos de componentes

---

**¡Listo!** Ahora tienes todo lo necesario para crear aplicaciones web con el diseño y estilo de Davivienda usando React y shadcn/ui.
