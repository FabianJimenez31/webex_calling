import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { AIBorder } from '../ui/ai-border';
import { AILoadingModal } from '../ui/ai-loading-modal';
import { Shield, AlertTriangle, Clock, Phone, Loader2, RefreshCw, AlertCircle } from 'lucide-react';

interface SecurityAlert {
  alert_type: string;
  severity: string;
  user: string;
  title: string;
  description: string;
  details: any;
  recommended_action: string;
  timestamp: string;
}

interface SecurityScanResult {
  alerts: SecurityAlert[];
  stats: {
    total_cdrs: number;
    suspicious_patterns: number;
    high_risk_calls: number;
    medium_risk_calls: number;
    low_risk_calls: number;
  };
  security_score: number;
  risk_level: string;
  analysis_period_hours: number;
  analyzed_users: number;
  timestamp: string;
}

export function SecurityDashboard() {
  const [scanResult, setScanResult] = useState<SecurityScanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [hours, setHours] = useState(24);
  const [showAIModal, setShowAIModal] = useState(false);

  useEffect(() => {
    runSecurityScan();
  }, []);

  const runSecurityScan = async () => {
    setLoading(true);
    setShowAIModal(true); // Show AI loading modal
    try {
      const startTime = Date.now();

      const response = await fetch(`/api/v1/analytics/security/scan?hours=${hours}&limit=1000`);
      const data = await response.json();

      // Ensure modal shows for at least 3 seconds
      const elapsedTime = Date.now() - startTime;
      const remainingTime = Math.max(0, 3000 - elapsedTime);
      await new Promise(resolve => setTimeout(resolve, remainingTime));

      setScanResult(data);
      setShowAIModal(false); // Hide modal

      // Scroll to top after loading data
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      console.error('Error running security scan:', error);
      setShowAIModal(false); // Hide modal on error
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    if (score >= 40) return 'bg-orange-100';
    return 'bg-red-100';
  };

  const getRiskLevelBadge = (level: string) => {
    const colors: Record<string, string> = {
      'SEGURO': 'bg-green-100 text-green-700 border-green-300',
      'BAJO': 'bg-green-50 text-green-600 border-green-200',
      'MEDIO': 'bg-yellow-50 text-yellow-700 border-yellow-300',
      'ALTO': 'bg-orange-100 text-orange-700 border-orange-300',
      'CRÍTICO': 'bg-red-100 text-red-700 border-red-300'
    };
    return colors[level] || 'bg-gray-100 text-gray-700';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-orange-600" />;
      case 'medium':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-blue-600" />;
    }
  };

  const getSeverityBadge = (severity: string) => {
    const colors: Record<string, string> = {
      'critical': 'bg-red-100 text-red-700 border-red-300',
      'high': 'bg-orange-100 text-orange-700 border-orange-300',
      'medium': 'bg-yellow-100 text-yellow-700 border-yellow-300',
      'low': 'bg-blue-100 text-blue-700 border-blue-300'
    };
    return colors[severity] || 'bg-gray-100 text-gray-700';
  };

  const getAlertTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'unusual_international_calls': 'Llamadas Internacionales Sospechosas',
      'after_hours_activity': 'Actividad Fuera de Horario',
      'mass_dialing': 'Mass Dialing (Ataque)',
      'rapid_sequential_calls': 'Llamadas Rápidas Secuenciales',
      'suspicious_call_forwarding': 'Destinos de Alto Costo'
    };
    return labels[type] || type;
  };

  if (loading && !scanResult) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-davivienda-red" />
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* AI Loading Modal */}
      <AILoadingModal
        isOpen={showAIModal}
        message="Analizando seguridad con IA..."
      />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-davivienda-black">Dashboard de Seguridad 🔒</h2>
          <p className="text-sm text-gray-600">Detección de fraude y análisis de patrones sospechosos</p>
        </div>
        <div className="flex gap-2 items-center">
          <select
            value={hours}
            onChange={(e) => setHours(Number(e.target.value))}
            className="px-3 py-2 border rounded-md text-sm"
          >
            <option value={24}>Últimas 24h</option>
            <option value={48}>Últimas 48h</option>
            <option value={72}>Últimas 72h</option>
            <option value={168}>Última semana</option>
          </select>
          <Button
            size="sm"
            onClick={runSecurityScan}
            disabled={loading}
            className="bg-davivienda-red hover:bg-davivienda-red/90"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Escaneando...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                Escanear
              </>
            )}
          </Button>
        </div>
      </div>

      {scanResult && (
        <>
          {/* Security Score Card */}
          <Card className="border-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Score de Seguridad</CardTitle>
                  <CardDescription>Nivel de riesgo general del sistema</CardDescription>
                </div>
                <Shield className={`h-10 w-10 ${getScoreColor(scanResult.security_score)}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-end gap-4">
                <div className={`text-6xl font-bold ${getScoreColor(scanResult.security_score)}`}>
                  {scanResult.security_score}
                </div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded-full overflow-hidden mb-2">
                    <div
                      className={`h-full ${getScoreBgColor(scanResult.security_score)}`}
                      style={{ width: `${scanResult.security_score}%` }}
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">Nivel de Riesgo:</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getRiskLevelBadge(scanResult.risk_level)}`}>
                      {scanResult.risk_level}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="border-l-4 border-l-red-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Alertas Críticas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-600">
                  {scanResult.stats.high_risk_calls}
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-yellow-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Alertas Medias</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-yellow-600">
                  {scanResult.stats.medium_risk_calls}
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-blue-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Patrones Sospechosos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">
                  {scanResult.stats.suspicious_patterns}
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-green-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Usuarios Analizados</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {scanResult.analyzed_users}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Alerts List */}
          <Card>
            <CardHeader>
              <CardTitle>Alertas de Seguridad ({scanResult.alerts.length})</CardTitle>
              <CardDescription>
                Patrones sospechosos detectados en las últimas {scanResult.analysis_period_hours} horas
              </CardDescription>
            </CardHeader>
            <CardContent>
              {scanResult.alerts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Shield className="h-12 w-12 mx-auto mb-3 text-green-500" />
                  <p className="font-semibold">✅ No se detectaron alertas de seguridad</p>
                  <p className="text-sm">El sistema está operando normalmente</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {scanResult.alerts.map((alert, idx) => (
                    <div
                      key={idx}
                      className={`border-l-4 p-4 rounded-r-lg ${
                        alert.severity === 'critical' ? 'border-l-red-500 bg-red-50' :
                        alert.severity === 'high' ? 'border-l-orange-500 bg-orange-50' :
                        alert.severity === 'medium' ? 'border-l-yellow-500 bg-yellow-50' :
                        'border-l-blue-500 bg-blue-50'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className="mt-1">
                          {getSeverityIcon(alert.severity)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`px-2 py-0.5 rounded text-xs font-semibold border ${getSeverityBadge(alert.severity)}`}>
                              {alert.severity.toUpperCase()}
                            </span>
                            <span className="text-xs text-gray-600">
                              {getAlertTypeLabel(alert.alert_type)}
                            </span>
                          </div>
                          <h4 className="font-semibold text-gray-900 mb-1">{alert.title}</h4>
                          <p className="text-sm text-gray-700 mb-2">{alert.description}</p>

                          {/* Alert Details */}
                          <div className="bg-white/50 rounded p-2 mb-2 text-xs">
                            <div className="grid grid-cols-2 gap-2">
                              {Object.entries(alert.details).map(([key, value]) => {
                                if (Array.isArray(value)) {
                                  return (
                                    <div key={key} className="col-span-2">
                                      <span className="font-semibold">{key}:</span>
                                      <span className="ml-2">{value.join(', ')}</span>
                                    </div>
                                  );
                                }
                                return (
                                  <div key={key}>
                                    <span className="font-semibold">{key}:</span>
                                    <span className="ml-2">{String(value)}</span>
                                  </div>
                                );
                              })}
                            </div>
                          </div>

                          {/* Recommended Action */}
                          <AIBorder borderWidth={2}>
                            <div className="bg-white rounded p-2 border border-gray-200">
                              <p className="text-xs font-semibold text-gray-700 mb-1">📋 Acción Recomendada IA:</p>
                              <p className="text-xs text-gray-600">{alert.recommended_action}</p>
                            </div>
                          </AIBorder>

                          {/* Timestamp */}
                          <div className="flex items-center gap-1 mt-2 text-xs text-gray-500">
                            <Clock className="h-3 w-3" />
                            <span>{new Date(alert.timestamp).toLocaleString()}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Detection Types Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Tipos de Detección Activos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
                <div className="flex items-start gap-2 p-2 bg-gray-50 rounded">
                  <Phone className="h-4 w-4 text-blue-600 mt-0.5" />
                  <div>
                    <div className="font-semibold">Llamadas Internacionales</div>
                    <div className="text-gray-600">≥5 llamadas en 1 hora</div>
                  </div>
                </div>
                <div className="flex items-start gap-2 p-2 bg-gray-50 rounded">
                  <Clock className="h-4 w-4 text-orange-600 mt-0.5" />
                  <div>
                    <div className="font-semibold">Fuera de Horario</div>
                    <div className="text-gray-600">≥3 llamadas (7PM-7AM)</div>
                  </div>
                </div>
                <div className="flex items-start gap-2 p-2 bg-gray-50 rounded">
                  <AlertTriangle className="h-4 w-4 text-red-600 mt-0.5" />
                  <div>
                    <div className="font-semibold">Mass Dialing</div>
                    <div className="text-gray-600">≥20 destinos únicos</div>
                  </div>
                </div>
                <div className="flex items-start gap-2 p-2 bg-gray-50 rounded">
                  <Shield className="h-4 w-4 text-purple-600 mt-0.5" />
                  <div>
                    <div className="font-semibold">Llamadas Rápidas</div>
                    <div className="text-gray-600">≥10 llamadas en 5 min</div>
                  </div>
                </div>
                <div className="flex items-start gap-2 p-2 bg-gray-50 rounded">
                  <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
                  <div>
                    <div className="font-semibold">Alto Costo</div>
                    <div className="text-gray-600">900, 888, 809, 876</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
