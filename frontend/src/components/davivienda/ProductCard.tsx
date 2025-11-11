/**
 * Product Card Component
 */
import React from 'react';

interface ProductCardProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  badge?: string;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  title,
  description,
  icon,
  badge
}) => {
  return (
    <div className="card-davivienda hover-lift relative">
      {badge && (
        <div className="absolute top-4 right-4">
          <span className="badge-davivienda">{badge}</span>
        </div>
      )}

      <div className="mb-4">
        {icon && (
          <div className="w-12 h-12 bg-davivienda-red-50 rounded-lg flex items-center justify-center mb-4">
            <div className="text-davivienda-red-500">
              {icon}
            </div>
          </div>
        )}
        <h3 className="text-h4 mb-2">{title}</h3>
        <p className="text-body text-muted-foreground">
          {description}
        </p>
      </div>

      <a href="#" className="link-davivienda font-medium flex items-center gap-2">
        Ver más
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </a>
    </div>
  );
};
