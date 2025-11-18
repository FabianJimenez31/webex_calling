import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { AlertCircle, CheckCircle, RefreshCw } from 'lucide-react';

export function AuthStatusBanner() {
  const [authStatus, setAuthStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
    // Check every 5 minutes
    const interval = setInterval(checkAuthStatus, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('/auth/status');
      const data = await response.json();
      setAuthStatus(data);
    } catch (error) {
      console.error('Error checking auth status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReauth = () => {
    window.location.href = '/auth/login';
  };

  if (loading) {
    return null;
  }

  // Don't show banner if everything is OK
  if (authStatus?.has_refresh_token && authStatus?.has_access_token && !authStatus?.is_expired) {
    return null;
  }

  // Show warning if missing refresh token or token is expired
  const needsAuth = !authStatus?.has_refresh_token || authStatus?.is_expired;

  return (
    <Card className={`mb-4 border-l-4 ${needsAuth ? 'border-l-orange-500 bg-orange-50' : 'border-l-yellow-500 bg-yellow-50'}`}>
      <CardContent className="py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {needsAuth ? (
              <AlertCircle className="h-5 w-5 text-orange-600" />
            ) : (
              <CheckCircle className="h-5 w-5 text-yellow-600" />
            )}
            <div>
              <p className="font-semibold text-sm">
                {needsAuth ? '⚠️ Autenticación Requerida' : 'Token de Acceso Limitado'}
              </p>
              <p className="text-xs text-gray-700 mt-1">
                {!authStatus?.has_refresh_token && (
                  <>No hay refresh token configurado. Los reportes y análisis no funcionarán correctamente.</>
                )}
                {authStatus?.is_expired && (
                  <>El token de acceso ha expirado. Por favor re-autentica con Webex.</>
                )}
              </p>
            </div>
          </div>
          <Button
            onClick={handleReauth}
            className="bg-davivienda-red hover:bg-davivienda-red/90 text-white"
            size="sm"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Re-autenticar con Webex
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
