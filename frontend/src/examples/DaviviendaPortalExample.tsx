/**
 * Davivienda Portal Example
 * This is a demo showcasing the Davivienda theme colors and components
 * Official colors: #E30519 (Shojo's Blood), #010101 (Binary Black), #F5F5F5 (Light Gray)
 */
import React from 'react';
import { DaviviendaHeader } from '../components/davivienda/Header';
import { DaviviendaHero } from '../components/davivienda/Hero';
import { ProductCard } from '../components/davivienda/ProductCard';
import { DaviviendaFooter } from '../components/davivienda/Footer';

export const DaviviendaPortalExample = () => {
  return (
    <div className="min-h-screen bg-background">
      <DaviviendaHeader />
      <DaviviendaHero />

      {/* Products Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-h2 mb-4">Productos y Servicios</h2>
          <p className="text-body-lg text-muted-foreground max-w-2xl mx-auto">
            Encuentra la solución financiera perfecta para ti
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <ProductCard
            title="Cuenta de Ahorros"
            description="Ahorra con nosotros y disfruta de los mejores beneficios. Sin cuota de manejo."
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
            badge="Popular"
          />

          <ProductCard
            title="Tarjeta de Crédito"
            description="Aprovecha nuestras tasas preferenciales y cupos desde $2.000.000."
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
            }
          />

          <ProductCard
            title="Crédito Hipotecario"
            description="Cumple tu sueño de casa propia con nuestros créditos de vivienda."
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            }
            badge="Nuevo"
          />
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-h2 text-davivienda-red-500 mb-2">8M+</div>
              <p className="text-body text-muted-foreground">Clientes</p>
            </div>
            <div>
              <div className="text-h2 text-davivienda-red-500 mb-2">800+</div>
              <p className="text-body text-muted-foreground">Oficinas</p>
            </div>
            <div>
              <div className="text-h2 text-davivienda-red-500 mb-2">24/7</div>
              <p className="text-body text-muted-foreground">Atención</p>
            </div>
            <div>
              <div className="text-h2 text-davivienda-red-500 mb-2">100%</div>
              <p className="text-body text-muted-foreground">Digital</p>
            </div>
          </div>
        </div>
      </section>

      <DaviviendaFooter />
    </div>
  );
};
