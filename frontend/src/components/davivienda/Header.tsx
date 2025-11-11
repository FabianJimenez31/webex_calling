/**
 * Header / Navbar Davivienda
 */
import React from 'react';

export const DaviviendaHeader = () => {
  return (
    <header className="header-davivienda sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="text-2xl font-bold text-davivienda-red-500">
              DAVIVIENDA
            </div>
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
