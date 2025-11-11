/**
 * Hero Section
 */
import React from 'react';

export const DaviviendaHero = () => {
  return (
    <section className="gradient-davivienda my-8">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-12 items-center py-16">
          <div className="space-y-6">
            <h1 className="text-h1 text-white">
              Tu banco digital,
              <span className="block">
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
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 h-96 flex items-center justify-center">
              <p className="text-white text-xl">Hero Image</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
