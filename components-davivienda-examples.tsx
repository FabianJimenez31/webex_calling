/**
 * Componentes de Ejemplo - Tema Davivienda
 * React + shadcn/ui
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

// ============================================================================
// 1. HEADER / NAVBAR DAVIVIENDA
// ============================================================================

export const DaviviendaHeader = () => {
  return (
    <header className="header-davivienda sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-18">
          {/* Logo */}
          <div className="flex items-center">
            <img
              src="/davivienda-logo.svg"
              alt="Davivienda"
              className="h-10"
            />
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#" className="text-foreground hover:text-davivienda-red-500 transition-colors font-medium">
              Personas
            </a>
            <a href="#" className="text-foreground hover:text-davivienda-red-500 transition-colors font-medium">
              Empresas
            </a>
            <a href="#" className="text-foreground hover:text-davivienda-red-500 transition-colors font-medium">
              Oficina Virtual
            </a>
            <a href="#" className="text-foreground hover:text-davivienda-red-500 transition-colors font-medium">
              Ayuda
            </a>
          </nav>

          {/* CTA Buttons */}
          <div className="flex items-center space-x-4">
            <button className="btn-davivienda-ghost text-sm">
              Ingresar
            </button>
            <button className="btn-davivienda-primary text-sm">
              Hazte Cliente
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

// ============================================================================
// 2. HERO SECTION
// ============================================================================

export const DaviviendaHero = () => {
  return (
    <section className="gradient-davivienda my-8">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <h1 className="text-h1 text-white">
              Tu banco digital,
              <span className="block text-davivienda-yellow-300">
                más cerca que nunca
              </span>
            </h1>
            <p className="text-body-lg text-white/90">
              Descubre todas las soluciones financieras que tenemos para ti.
              Cuentas, tarjetas, créditos y más, todo en un solo lugar.
            </p>
            <div className="flex flex-wrap gap-4">
              <button className="bg-white text-davivienda-red-500 px-8 py-4 rounded-lg font-semibold hover:bg-gray-50 transition-all shadow-lg">
                Abrir Cuenta
              </button>
              <button className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white/10 transition-all">
                Conocer Más
              </button>
            </div>
          </div>
          <div className="hidden md:block">
            {/* Placeholder for hero image */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 h-96" />
          </div>
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// 3. PRODUCT CARDS
// ============================================================================

interface ProductCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  badge?: string;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  title,
  description,
  icon,
  badge
}) => {
  return (
    <Card className="card-davivienda hover-lift relative">
      {badge && (
        <div className="absolute top-4 right-4">
          <Badge className="badge-davivienda">{badge}</Badge>
        </div>
      )}

      <CardHeader>
        <div className="w-12 h-12 bg-davivienda-red-50 rounded-lg flex items-center justify-center mb-4">
          <div className="text-davivienda-red-500">
            {icon}
          </div>
        </div>
        <CardTitle className="text-h4">{title}</CardTitle>
        <CardDescription className="text-body">
          {description}
        </CardDescription>
      </CardHeader>

      <CardFooter>
        <button className="link-davivienda font-medium flex items-center gap-2">
          Ver más
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </CardFooter>
    </Card>
  );
};

// ============================================================================
// 4. PRODUCTS GRID
// ============================================================================

export const ProductsGrid = () => {
  const products = [
    {
      title: "Cuenta de Ahorros",
      description: "Abre tu cuenta 100% digital y comienza a ahorrar desde hoy.",
      icon: <CreditCardIcon />,
      badge: "Nuevo"
    },
    {
      title: "Crédito de Libre Inversión",
      description: "Financia tus proyectos con tasas preferenciales.",
      icon: <MoneyIcon />,
    },
    {
      title: "Tarjeta de Crédito",
      description: "Disfruta de beneficios exclusivos y puntos por compras.",
      icon: <CardIcon />,
    },
    {
      title: "CDT Digital",
      description: "Invierte tu dinero de forma segura con rendimientos atractivos.",
      icon: <ChartIcon />,
      badge: "Popular"
    },
  ];

  return (
    <section className="py-16">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-h2 mb-4">Nuestros Productos</h2>
          <p className="text-body-lg text-muted-foreground max-w-2xl mx-auto">
            Soluciones financieras diseñadas para cada etapa de tu vida
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {products.map((product, index) => (
            <ProductCard key={index} {...product} />
          ))}
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// 5. FORM EXAMPLE
// ============================================================================

export const DaviviendaContactForm = () => {
  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="text-h3">Contáctanos</CardTitle>
        <CardDescription>
          Déjanos tus datos y te contactaremos pronto
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-2 block">
            Nombre Completo
          </label>
          <Input
            type="text"
            placeholder="Juan Pérez"
            className="input-davivienda"
          />
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">
            Correo Electrónico
          </label>
          <Input
            type="email"
            placeholder="tu@email.com"
            className="input-davivienda"
          />
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">
            Teléfono
          </label>
          <Input
            type="tel"
            placeholder="+57 300 123 4567"
            className="input-davivienda"
          />
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">
            Mensaje
          </label>
          <textarea
            rows={4}
            placeholder="Cuéntanos cómo podemos ayudarte"
            className="input-davivienda w-full resize-none"
          />
        </div>
      </CardContent>

      <CardFooter>
        <button className="btn-davivienda-primary w-full">
          Enviar Mensaje
        </button>
      </CardFooter>
    </Card>
  );
};

// ============================================================================
// 6. STATS SECTION
// ============================================================================

export const DaviviendaStats = () => {
  const stats = [
    { value: "12M+", label: "Clientes" },
    { value: "850+", label: "Oficinas" },
    { value: "3,200+", label: "Cajeros" },
    { value: "24/7", label: "Atención" },
  ];

  return (
    <section className="bg-davivienda-red-500 py-16">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          {stats.map((stat, index) => (
            <div key={index} className="space-y-2">
              <div className="text-h1 text-white font-bold">
                {stat.value}
              </div>
              <div className="text-body text-white/90">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// ============================================================================
// 7. FOOTER
// ============================================================================

export const DaviviendaFooter = () => {
  return (
    <footer className="bg-[#2C2C2C] text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="text-h5 mb-4">Productos</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-muted-foreground hover:text-white transition-colors">Cuentas</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-white transition-colors">Tarjetas</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-white transition-colors">Créditos</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-white transition-colors">Inversiones</a></li>
            </ul>
          </div>

          <div>
            <h3 className="text-h5 mb-4">Servicios</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-muted-foreground hover:text-white transition-colors">Oficina Virtual</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-white transition-colors">App Móvil</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-white transition-colors">Corresponsales</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-white transition-colors">PSE</a></li>
            </ul>
          </div>

          <div>
            <h3 className="text-h5 mb-4">Ayuda</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-muted-foreground hover:text-white transition-colors">Preguntas Frecuentes</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-white transition-colors">Chat en Línea</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-white transition-colors">Línea de Atención</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-white transition-colors">PQRS</a></li>
            </ul>
          </div>

          <div>
            <h3 className="text-h5 mb-4">Síguenos</h3>
            <div className="flex gap-4">
              <a href="#" className="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-colors">
                <span className="sr-only">Facebook</span>
                📘
              </a>
              <a href="#" className="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-colors">
                <span className="sr-only">Twitter</span>
                🐦
              </a>
              <a href="#" className="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-colors">
                <span className="sr-only">Instagram</span>
                📷
              </a>
            </div>
          </div>
        </div>

        <div className="border-t border-white/10 pt-8 text-center text-muted-foreground text-sm">
          <p>&copy; 2025 Banco Davivienda. Todos los derechos reservados.</p>
        </div>
      </div>
    </footer>
  );
};

// ============================================================================
// ICON COMPONENTS (Placeholder)
// ============================================================================

const CreditCardIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
  </svg>
);

const MoneyIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const CardIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
  </svg>
);

const ChartIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 00-2-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
  </svg>
);

// ============================================================================
// FULL PAGE EXAMPLE
// ============================================================================

export const DaviviendaExamplePage = () => {
  return (
    <div className="min-h-screen bg-background">
      <DaviviendaHeader />
      <DaviviendaHero />
      <ProductsGrid />
      <DaviviendaStats />

      <section className="py-16 bg-muted">
        <div className="container mx-auto px-4">
          <DaviviendaContactForm />
        </div>
      </section>

      <DaviviendaFooter />
    </div>
  );
};

export default DaviviendaExamplePage;
