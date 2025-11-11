/**
 * Footer Component
 */
import React from 'react';

export const DaviviendaFooter = () => {
  return (
    <footer className="bg-[#2C2C2C] text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 className="text-h5 mb-4">Productos</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Cuentas</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Tarjetas</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Créditos</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Inversiones</a></li>
            </ul>
          </div>

          <div>
            <h3 className="text-h5 mb-4">Servicios</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Oficina Virtual</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">App Móvil</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Corresponsales</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">PSE</a></li>
            </ul>
          </div>

          <div>
            <h3 className="text-h5 mb-4">Ayuda</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Preguntas Frecuentes</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Chat en Línea</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Línea de Atención</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">PQRS</a></li>
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

        <div className="border-t border-white/10 pt-8 text-center text-gray-400 text-sm">
          <p>&copy; 2025 Banco Davivienda. Todos los derechos reservados.</p>
        </div>
      </div>
    </footer>
  );
};
