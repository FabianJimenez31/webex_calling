import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { AIBorder } from '../ui/ai-border';
import { AILoadingModal } from '../ui/ai-loading-modal';
import { Users, TrendingUp, Clock, AlertTriangle, Loader2, RefreshCw, Calendar } from 'lucide-react';

interface StaffingRecommendation {
  hour: number;
  hour_label: string;
  call_volume: number;
  recommended_agents: number;
  priority: string;
}

interface StaffingData {
  recommendations: StaffingRecommendation[];
  peak_hours: StaffingRecommendation[];
  total_hours_coverage: number;
  summary: string;
  analysis_period_hours: number;
  total_calls_analyzed: number;
}

export function StaffingRecommendations() {
  const [staffingData, setStaffingData] = useState<StaffingData | null>(null);
  const [loading, setLoading] = useState(false);
  const [hours, setHours] = useState(168); // Default 7 days
  const [showAIModal, setShowAIModal] = useState(false);

  useEffect(() => {
    loadStaffingData();
  }, []);

  const loadStaffingData = async () => {
    setLoading(true);
    setShowAIModal(true); // Show AI loading modal
    try {
      const startTime = Date.now();

      const response = await fetch(`/api/v1/analytics/staffing/recommendations?hours=${hours}&limit=5000`);
      const data = await response.json();

      // Ensure modal shows for at least 3 seconds
      const elapsedTime = Date.now() - startTime;
      const remainingTime = Math.max(0, 3000 - elapsedTime);
      await new Promise(resolve => setTimeout(resolve, remainingTime));

      setStaffingData(data);
      setShowAIModal(false); // Hide modal

      // Scroll to top after loading data
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (error) {
      console.error('Error loading staffing data:', error);
      setShowAIModal(false); // Hide modal on error
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'ALTA':
        return 'bg-red-100 text-red-700 border-red-300';
      case 'MEDIA':
        return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'BAJA':
        return 'bg-green-100 text-green-700 border-green-300';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const getPriorityBadge = (priority: string) => {
    const icons = {
      'ALTA': '🔴',
      'MEDIA': '🟡',
      'BAJA': '🟢'
    };
    return icons[priority as keyof typeof icons] || '⚪';
  };

  const getVolumeBarHeight = (volume: number, maxVolume: number) => {
    return Math.max((volume / maxVolume) * 100, 5); // Min 5% for visibility
  };

  const maxVolume = staffingData ? Math.max(...staffingData.recommendations.map(r => r.call_volume)) : 1;

  if (loading && !staffingData) {
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
        message="Generando recomendaciones de staffing con IA..."
      />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-davivienda-black">Recomendaciones de Staffing ⏱️</h2>
          <p className="text-sm text-gray-600">Optimización de asignación de personal por hora</p>
        </div>
        <div className="flex gap-2 items-center">
          <select
            value={hours}
            onChange={(e) => setHours(Number(e.target.value))}
            className="px-3 py-2 border rounded-md text-sm"
          >
            <option value={168}>Última semana (recomendado)</option>
            <option value={336}>Últimas 2 semanas</option>
            <option value={720}>Último mes</option>
          </select>
          <Button
            size="sm"
            onClick={loadStaffingData}
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

      {staffingData && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="border-l-4 border-l-blue-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Período Analizado
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">
                  {staffingData.analysis_period_hours / 24} días
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  {staffingData.total_calls_analyzed} llamadas
                </p>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-purple-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Horas Cubiertas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-purple-600">
                  {staffingData.total_hours_coverage}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  horas del día
                </p>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-red-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4" />
                  Horas Pico
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-600">
                  {staffingData.peak_hours.length}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  prioridad alta
                </p>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-green-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  Máx Agentes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {Math.max(...staffingData.recommendations.map(r => r.recommended_agents))}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  agentes necesarios
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Summary Alert */}
          <AIBorder borderWidth={3}>
            <Card className="border-l-4 border-l-blue-500 bg-blue-50">
              <CardContent className="pt-4">
                <div className="flex items-start gap-3">
                  <TrendingUp className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-blue-900 mb-1">Resumen del Análisis IA</h3>
                    <p className="text-sm text-blue-800">{staffingData.summary}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </AIBorder>

          {/* Visual Call Volume Chart */}
          <Card>
            <CardHeader>
              <CardTitle>📊 Volumen de Llamadas por Hora</CardTitle>
              <CardDescription>Distribución de llamadas en un día típico</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-end justify-between gap-1 h-64">
                {Array.from({ length: 24 }, (_, i) => {
                  const rec = staffingData.recommendations.find(r => r.hour === i);
                  const volume = rec?.call_volume || 0;
                  const priority = rec?.priority || 'BAJA';
                  const height = getVolumeBarHeight(volume, maxVolume);

                  return (
                    <div key={i} className="flex-1 flex flex-col items-center justify-end gap-1 group relative">
                      {/* Tooltip */}
                      <div className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-900 text-white text-xs rounded p-2 z-10 whitespace-nowrap">
                        <div className="font-semibold">{i}:00 - {i + 1}:00</div>
                        <div>Volumen: {volume} llamadas</div>
                        {rec && <div>Agentes: {rec.recommended_agents}</div>}
                        <div className="mt-1">Prioridad: {priority}</div>
                      </div>

                      {/* Bar */}
                      <div
                        className={`w-full rounded-t transition-all ${
                          priority === 'ALTA' ? 'bg-red-500 hover:bg-red-600' :
                          priority === 'MEDIA' ? 'bg-yellow-500 hover:bg-yellow-600' :
                          'bg-green-500 hover:bg-green-600'
                        }`}
                        style={{ height: `${height}%` }}
                      />

                      {/* Hour Label */}
                      <div className="text-xs text-gray-600 font-medium">
                        {i}
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-center gap-4 mt-4 text-xs">
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 bg-red-500 rounded"></div>
                  <span>Alta Prioridad</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                  <span>Media Prioridad</span>
                </div>
                <div className="flex items-center gap-1">
                  <div className="w-3 h-3 bg-green-500 rounded"></div>
                  <span>Baja Prioridad</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Peak Hours Detail */}
          {staffingData.peak_hours.length > 0 && (
            <AIBorder borderWidth={3}>
              <Card className="border-2 border-red-200">
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-red-600" />
                    Horas Pico - Prioridad Alta (Recomendación IA)
                  </CardTitle>
                  <CardDescription>
                    Estas horas requieren mayor cobertura de personal
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {staffingData.peak_hours.map((rec, idx) => (
                      <div
                        key={idx}
                        className="p-4 bg-red-50 border border-red-200 rounded-lg"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="font-bold text-red-900">{rec.hour_label}</div>
                          <span className="text-2xl">{getPriorityBadge(rec.priority)}</span>
                        </div>
                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Volumen:</span>
                            <span className="font-semibold text-red-700">{rec.call_volume} llamadas</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Agentes necesarios:</span>
                            <span className="font-semibold text-red-700">{rec.recommended_agents}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </AIBorder>
          )}

          {/* Detailed Recommendations Table */}
          <Card>
            <CardHeader>
              <CardTitle>📋 Tabla de Recomendaciones Completa</CardTitle>
              <CardDescription>
                Recomendaciones de staffing para todas las horas del día
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100 border-b">
                    <tr>
                      <th className="px-4 py-2 text-left">Hora</th>
                      <th className="px-4 py-2 text-center">Volumen</th>
                      <th className="px-4 py-2 text-center">Agentes Recomendados</th>
                      <th className="px-4 py-2 text-center">Prioridad</th>
                      <th className="px-4 py-2 text-center">Llamadas/Agente</th>
                    </tr>
                  </thead>
                  <tbody>
                    {staffingData.recommendations.map((rec, idx) => (
                      <tr
                        key={idx}
                        className={`border-b hover:bg-gray-50 ${
                          rec.priority === 'ALTA' ? 'bg-red-50' :
                          rec.priority === 'MEDIA' ? 'bg-yellow-50' :
                          ''
                        }`}
                      >
                        <td className="px-4 py-3 font-medium">
                          {rec.hour_label}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <div className="inline-flex items-center gap-2">
                            <div
                              className="h-2 bg-blue-500 rounded"
                              style={{ width: `${(rec.call_volume / maxVolume) * 50}px` }}
                            />
                            <span className="font-semibold">{rec.call_volume}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <div className="flex items-center justify-center gap-1">
                            <Users className="h-4 w-4 text-gray-600" />
                            <span className="font-bold text-lg">{rec.recommended_agents}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getPriorityColor(rec.priority)}`}>
                            {getPriorityBadge(rec.priority)} {rec.priority}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center text-gray-600">
                          {(rec.call_volume / rec.recommended_agents).toFixed(1)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Staffing Strategy Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">📖 Estrategia de Staffing</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="p-4 bg-gray-50 rounded">
                  <h4 className="font-semibold mb-2 flex items-center gap-2">
                    <Clock className="h-4 w-4 text-blue-600" />
                    Cálculo Base
                  </h4>
                  <p className="text-gray-700">
                    Se asume una capacidad de <strong>10 llamadas por agente por hora</strong>.
                    Las recomendaciones se ajustan automáticamente según el volumen histórico.
                  </p>
                </div>
                <div className="p-4 bg-gray-50 rounded">
                  <h4 className="font-semibold mb-2 flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    Prioridades
                  </h4>
                  <ul className="text-gray-700 space-y-1">
                    <li>• <strong>ALTA:</strong> &gt;15 llamadas/hora</li>
                    <li>• <strong>MEDIA:</strong> 5-15 llamadas/hora</li>
                    <li>• <strong>BAJA:</strong> &lt;5 llamadas/hora</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
