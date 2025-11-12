import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { CheckCircle, XCircle, AlertCircle, TrendingUp, Clock, Users, Loader2, RefreshCw } from 'lucide-react';

interface SLAMetric {
  value: number;
  target: number;
  compliant: boolean;
  status: string;
}

interface SLAComplianceData {
  answer_rate: SLAMetric;
  avg_handle_time: SLAMetric;
  team_compliance: SLAMetric;
  overall_score: number;
  overall_status: string;
  analysis_period_hours: number;
  total_agents_analyzed: number;
  total_calls_analyzed: number;
}

export function SLAComplianceView() {
  const [slaData, setSlaData] = useState<SLAComplianceData | null>(null);
  const [loading, setLoading] = useState(false);
  const [hours, setHours] = useState(24);

  useEffect(() => {
    loadSLAData();
  }, []);

  const loadSLAData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/analytics/sla/compliance?hours=${hours}&limit=1000`);
      const data = await response.json();
      setSlaData(data);
    } catch (error) {
      console.error('Error loading SLA data:', error);
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
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    if (score >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getStatusIcon = (compliant: boolean) => {
    return compliant ? (
      <CheckCircle className="h-6 w-6 text-green-600" />
    ) : (
      <XCircle className="h-6 w-6 text-red-600" />
    );
  };

  const getProgressColor = (value: number, target: number, inverse: boolean = false) => {
    const percentage = inverse ? (target / value) * 100 : (value / target) * 100;
    if (percentage >= 100) return 'bg-green-500';
    if (percentage >= 80) return 'bg-yellow-500';
    if (percentage >= 60) return 'bg-orange-500';
    return 'bg-red-500';
  };

  if (loading && !slaData) {
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-davivienda-black">Cumplimiento de SLA ✅</h2>
          <p className="text-sm text-gray-600">Monitoreo de Service Level Agreements</p>
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
            onClick={loadSLAData}
            disabled={loading}
            className="bg-davivienda-red hover:bg-davivienda-red/90"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Cargando...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                Actualizar
              </>
            )}
          </Button>
        </div>
      </div>

      {slaData && (
        <>
          {/* Overall SLA Score */}
          <Card className={`border-4 ${
            slaData.overall_score >= 80 ? 'border-green-300 bg-green-50' :
            slaData.overall_score >= 60 ? 'border-yellow-300 bg-yellow-50' :
            'border-red-300 bg-red-50'
          }`}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Score General de SLA</span>
                <span className="text-4xl">{slaData.overall_status}</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-6">
                <div className={`text-7xl font-bold ${getScoreColor(slaData.overall_score)}`}>
                  {slaData.overall_score}
                </div>
                <div className="flex-1">
                  <div className="h-8 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={getScoreBgColor(slaData.overall_score)}
                      style={{ width: `${slaData.overall_score}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-sm text-gray-600 mt-2">
                    <span>0</span>
                    <span>50</span>
                    <span>80 (Target)</span>
                    <span>100</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="border-l-4 border-l-blue-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Período Analizado
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">
                  {slaData.analysis_period_hours}h
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  {new Date(Date.now() - slaData.analysis_period_hours * 3600000).toLocaleDateString()} - Hoy
                </p>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-purple-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  Agentes Analizados
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-purple-600">
                  {slaData.total_agents_analyzed}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  Agentes activos
                </p>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-green-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  Llamadas Analizadas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {slaData.total_calls_analyzed}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  Total de llamadas
                </p>
              </CardContent>
            </Card>
          </div>

          {/* SLA Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Answer Rate */}
            <Card className={`border-2 ${
              slaData.answer_rate.compliant ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'
            }`}>
              <CardHeader>
                <CardTitle className="text-base flex items-center justify-between">
                  <span>Answer Rate</span>
                  {getStatusIcon(slaData.answer_rate.compliant)}
                </CardTitle>
                <CardDescription>{slaData.answer_rate.status}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-baseline gap-2">
                    <div className={`text-4xl font-bold ${
                      slaData.answer_rate.compliant ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {slaData.answer_rate.value.toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">
                      / {slaData.answer_rate.target}% target
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span>Progreso</span>
                      <span>{((slaData.answer_rate.value / slaData.answer_rate.target) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={getProgressColor(slaData.answer_rate.value, slaData.answer_rate.target)}
                        style={{ width: `${Math.min((slaData.answer_rate.value / slaData.answer_rate.target) * 100, 100)}%` }}
                      />
                    </div>
                  </div>

                  <div className="text-xs text-gray-600 bg-white/50 p-2 rounded">
                    <strong>Objetivo:</strong> Contestar al menos {slaData.answer_rate.target}% de las llamadas entrantes
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Avg Handle Time */}
            <Card className={`border-2 ${
              slaData.avg_handle_time.compliant ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'
            }`}>
              <CardHeader>
                <CardTitle className="text-base flex items-center justify-between">
                  <span>Avg Handle Time</span>
                  {getStatusIcon(slaData.avg_handle_time.compliant)}
                </CardTitle>
                <CardDescription>{slaData.avg_handle_time.status}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-baseline gap-2">
                    <div className={`text-4xl font-bold ${
                      slaData.avg_handle_time.compliant ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {slaData.avg_handle_time.value.toFixed(0)}s
                    </div>
                    <div className="text-sm text-gray-600">
                      / {slaData.avg_handle_time.target}s target
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span>Eficiencia</span>
                      <span>{slaData.avg_handle_time.compliant ? '✅ Dentro del objetivo' : '⚠️ Por encima'}</span>
                    </div>
                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={getProgressColor(slaData.avg_handle_time.value, slaData.avg_handle_time.target, true)}
                        style={{ width: `${Math.min((slaData.avg_handle_time.target / slaData.avg_handle_time.value) * 100, 100)}%` }}
                      />
                    </div>
                  </div>

                  <div className="text-xs text-gray-600 bg-white/50 p-2 rounded">
                    <strong>Objetivo:</strong> Mantener tiempo promedio de manejo bajo {slaData.avg_handle_time.target} segundos (3 min)
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Team Compliance */}
            <Card className={`border-2 ${
              slaData.team_compliance.compliant ? 'border-green-300 bg-green-50' : 'border-yellow-300 bg-yellow-50'
            }`}>
              <CardHeader>
                <CardTitle className="text-base flex items-center justify-between">
                  <span>Team Compliance</span>
                  {slaData.team_compliance.compliant ? (
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  ) : (
                    <AlertCircle className="h-6 w-6 text-yellow-600" />
                  )}
                </CardTitle>
                <CardDescription>{slaData.team_compliance.status}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-baseline gap-2">
                    <div className={`text-4xl font-bold ${
                      slaData.team_compliance.compliant ? 'text-green-600' : 'text-yellow-600'
                    }`}>
                      {slaData.team_compliance.value.toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-600">
                      / {slaData.team_compliance.target}% target
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span>Progreso</span>
                      <span>{((slaData.team_compliance.value / slaData.team_compliance.target) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={getProgressColor(slaData.team_compliance.value, slaData.team_compliance.target)}
                        style={{ width: `${Math.min((slaData.team_compliance.value / slaData.team_compliance.target) * 100, 100)}%` }}
                      />
                    </div>
                  </div>

                  <div className="text-xs text-gray-600 bg-white/50 p-2 rounded">
                    <strong>Objetivo:</strong> Al menos {slaData.team_compliance.target}% de los agentes deben cumplir con SLA individual
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* SLA Targets Reference */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">📋 Targets de SLA Configurados</CardTitle>
              <CardDescription>Objetivos definidos para el equipo</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                <div className="p-3 bg-blue-50 rounded border border-blue-200">
                  <div className="font-semibold text-blue-900 mb-1">Answer Time Target</div>
                  <div className="text-2xl font-bold text-blue-600">20s</div>
                  <div className="text-xs text-blue-700 mt-1">Tiempo objetivo de respuesta</div>
                </div>
                <div className="p-3 bg-green-50 rounded border border-green-200">
                  <div className="font-semibold text-green-900 mb-1">Answer Rate Target</div>
                  <div className="text-2xl font-bold text-green-600">80%</div>
                  <div className="text-xs text-green-700 mt-1">Tasa de contestación objetivo</div>
                </div>
                <div className="p-3 bg-purple-50 rounded border border-purple-200">
                  <div className="font-semibold text-purple-900 mb-1">Avg Handle Time Target</div>
                  <div className="text-2xl font-bold text-purple-600">180s</div>
                  <div className="text-xs text-purple-700 mt-1">Tiempo promedio de manejo</div>
                </div>
                <div className="p-3 bg-orange-50 rounded border border-orange-200">
                  <div className="font-semibold text-orange-900 mb-1">Abandonment Rate Target</div>
                  <div className="text-2xl font-bold text-orange-600">10%</div>
                  <div className="text-xs text-orange-700 mt-1">Máx tasa de abandono</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Card className="border-l-4 border-l-davivienda-red">
            <CardHeader>
              <CardTitle className="text-base">💡 Recomendaciones</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                {!slaData.answer_rate.compliant && (
                  <div className="p-3 bg-red-50 rounded border border-red-200 text-red-800">
                    <strong>⚠️ Answer Rate Bajo:</strong> Considere aumentar el personal o revisar los procesos de routing de llamadas.
                  </div>
                )}
                {!slaData.avg_handle_time.compliant && (
                  <div className="p-3 bg-yellow-50 rounded border border-yellow-200 text-yellow-800">
                    <strong>⏱️ Handle Time Alto:</strong> Revisar scripts de agentes y capacitación para mejorar eficiencia.
                  </div>
                )}
                {!slaData.team_compliance.compliant && (
                  <div className="p-3 bg-orange-50 rounded border border-orange-200 text-orange-800">
                    <strong>👥 Team Compliance Bajo:</strong> Identificar agentes con bajo rendimiento y proporcionar coaching.
                  </div>
                )}
                {slaData.overall_score >= 80 && (
                  <div className="p-3 bg-green-50 rounded border border-green-200 text-green-800">
                    <strong>✅ Excelente Desempeño:</strong> El equipo está cumpliendo con todos los objetivos de SLA. Mantener estas prácticas.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
