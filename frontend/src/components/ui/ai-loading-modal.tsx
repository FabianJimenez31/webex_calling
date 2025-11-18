import React from 'react';
import { Brain, Sparkles } from 'lucide-react';

interface AILoadingModalProps {
  isOpen: boolean;
  message?: string;
}

/**
 * Modal de loading que muestra mientras la IA genera recomendaciones
 */
export function AILoadingModal({ isOpen, message = 'Generando recomendaciones con IA...' }: AILoadingModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="relative">
        {/* Animated border around the modal */}
        <div
          className="absolute inset-0 rounded-2xl animate-border-gradient"
          style={{
            background: 'conic-gradient(from var(--gradient-angle), #EC0000 0deg, #FF1744 90deg, #00E5FF 180deg, #00B0FF 270deg, #EC0000 360deg)',
            padding: '4px',
            WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'xor',
            mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            maskComposite: 'exclude',
          }}
        />

        {/* Modal content */}
        <div className="relative bg-white dark:bg-gray-900 rounded-2xl p-8 shadow-2xl">
          <div className="flex flex-col items-center gap-6 min-w-[300px]">
            {/* Brain icon with pulse animation */}
            <div className="relative">
              <Brain className="h-16 w-16 text-davivienda-red animate-pulse" />
              <div className="absolute inset-0 bg-davivienda-red/20 rounded-full animate-ping" />

              {/* Sparkles around */}
              <Sparkles className="absolute -top-2 -right-2 h-6 w-6 text-yellow-500 animate-pulse" style={{ animationDelay: '0.3s' }} />
              <Sparkles className="absolute -bottom-2 -left-2 h-5 w-5 text-blue-500 animate-pulse" style={{ animationDelay: '0.6s' }} />
            </div>

            {/* Loading text */}
            <div className="text-center space-y-2">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">
                {message}
              </h3>

              {/* Animated dots */}
              <div className="flex justify-center gap-2">
                <span className="w-2 h-2 bg-davivienda-red rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-davivienda-red rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-davivienda-red rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-davivienda-red via-pink-500 to-blue-500 animate-pulse"
                style={{ width: '100%' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
