import React from 'react';

interface AIBorderProps {
  children: React.ReactNode;
  className?: string;
  borderWidth?: number;
}

/**
 * Componente que envuelve contenido con un borde animado estilo Apple Intelligence
 * para indicar que el contenido es generado o asistido por IA
 */
export function AIBorder({
  children,
  className = '',
  borderWidth = 3
}: AIBorderProps) {
  return (
    <div className={`relative rounded-lg ${className}`}>
      {/* Animated gradient border - gradient travels around the border */}
      <div
        className="absolute inset-0 rounded-lg animate-border-gradient"
        style={{
          background: 'conic-gradient(from var(--gradient-angle), #EC0000 0deg, #FF1744 90deg, #00E5FF 180deg, #00B0FF 270deg, #EC0000 360deg)',
          padding: `${borderWidth}px`,
          WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
          WebkitMaskComposite: 'xor',
          mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
          maskComposite: 'exclude',
        }}
      />

      {/* Content - stays static */}
      <div className="relative">
        {children}
      </div>
    </div>
  );
}
