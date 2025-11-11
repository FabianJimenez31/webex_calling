import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Users, TrendingUp, Phone, Clock, Award, CheckCircle, XCircle, Loader2, RefreshCw } from 'lucide-react';

interface AgentMetrics {
  agent: string;
  total_calls: number;
  calls_answered: number;
  calls_failed: number;
  answer_rate: number;
  inbound_calls: number;
  outbound_calls: number;
  total_duration_seconds: number;
  total_duration_minutes: number;
  avg_handle_time: number;
  min_duration: number;
  max_duration: number;
  hour_distribution: Record<number, number>;
  productivity_score: number;
  sla_compliant: boolean;
}

interface OverallMetrics {
  total_agents: number;
  total_calls: number;
  total_answered: number;
  total_failed: number;
  overall_answer_rate: number;
  avg_handle_time: number;
  avg_productivity_score: number;
  sla_violations: number;
  sla_compliance_rate: number;
}

interface PerformanceResult {
  agents: AgentMetrics[];
  overall: OverallMetrics;
  insights: string[];
  sla_compliance: any;
  analysis_period_hours: number;
  timestamp: string;
}

export function AgentPerformanceDashboard() {
  const [performanceData, setPerformanceData] = useState<PerformanceResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [hours, setHours] = useState(24);

  useEffect(() => {
    loadPerformanceData();
  }, []);

  const loadPerformanceData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/analytics/agents/performance?hours=${hours}&limit=1000`);
      const data = await response.json();
      setPerformanceData(data);
    } catch (error) {
      console.error('Error loading performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProductivityColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProductivityBg = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-blue-100';
    if (score >= 40) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  if (loading && !performanceData) {
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
          <h2 className="text-2xl font-bold text-davivienda-black">Performance de Agentes 👥</h2>
          <p className="text-sm text-gray-600">Análisis de productividad y eficiencia del equipo</p>
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
            onClick={loadPerformanceData}
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

      {performanceData && (
        <>
          {/* Overall Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="border-l-4 border-l-blue-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  Total Agentes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">
                  {performanceData.overall.total_agents}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  {performanceData.overall.sla_violations} violaciones SLA
                </p>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-green-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <Phone className="h-4 w-4" />
                  Llamadas Totales
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">
                  {performanceData.overall.total_calls}
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  {performanceData.overall.total_answered} contestadas
                </p>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-purple-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  Answer Rate
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-purple-600">
                  {performanceData.overall.overall_answer_rate}%
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  Target: 80%
                </p>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-orange-500">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Avg Handle Time
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-600">
                  {Math.round(performanceData.overall.avg_handle_time)}s
                </div>
                <p className="text-xs text-gray-600 mt-1">
                  Target: 180s
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Team Productivity Score */}
          <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="h-5 w-5 text-blue-600" />
                Score de Productividad del Equipo
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4">
                <div className={`text-5xl font-bold ${getProductivityColor(performanceData.overall.avg_productivity_score)}`}>
                  {performanceData.overall.avg_productivity_score.toFixed(1)}
                </div>
                <div className="flex-1">
                  <div className="h-6 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getProductivityBg(performanceData.overall.avg_productivity_score)}`}
                      style={{ width: `${performanceData.overall.avg_productivity_score}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-gray-600 mt-1">
                    <span>0</span>
                    <span>50</span>
                    <span>100</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Insights */}
          {performanceData.insights.length > 0 && (
            <Card className="border-l-4 border-l-blue-500">
              <CardHeader>
                <CardTitle className="text-base">💡 Observaciones Clave</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {performanceData.insights.map((insight, idx) => (
                    <div key={idx} className="flex items-start gap-2 p-2 bg-blue-50 rounded text-sm">
                      <span className="text-blue-600 mt-0.5">•</span>
                      <span className="text-gray-700">{insight}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Top Performers Table */}
          <Card>
            <CardHeader>
              <CardTitle>🏆 Top Performers</CardTitle>
              <CardDescription>
                Top {Math.min(10, performanceData.agents.length)} agentes por llamadas atendidas
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100 border-b">
                    <tr>
                      <th className="px-4 py-2 text-left">#</th>
                      <th className="px-4 py-2 text-left">Agente</th>
                      <th className="px-4 py-2 text-center">Llamadas</th>
                      <th className="px-4 py-2 text-center">Contestadas</th>
                      <th className="px-4 py-2 text-center">Answer Rate</th>
                      <th className="px-4 py-2 text-center">Avg Handle Time</th>
                      <th className="px-4 py-2 text-center">Productividad</th>
                      <th className="px-4 py-2 text-center">SLA</th>
                    </tr>
                  </thead>
                  <tbody>
                    {performanceData.agents.slice(0, 10).map((agent, idx) => (
                      <tr key={idx} className="border-b hover:bg-gray-50">
                        <td className="px-4 py-3 font-semibold text-gray-600">
                          {idx + 1}
                        </td>
                        <td className="px-4 py-3 font-medium">
                          {agent.agent}
                        </td>
                        <td className="px-4 py-3 text-center">
                          {agent.total_calls}
                        </td>
                        <td className="px-4 py-3 text-center text-green-600 font-semibold">
                          {agent.calls_answered}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className={`px-2 py-1 rounded ${
                            agent.answer_rate >= 80 ? 'bg-green-100 text-green-700' :
                            agent.answer_rate >= 60 ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700'
                          }`}>
                            {agent.answer_rate}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          {formatDuration(Math.round(agent.avg_handle_time))}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <div className="flex items-center gap-2 justify-center">
                            <div className={`text-lg font-bold ${getProductivityColor(agent.productivity_score)}`}>
                              {agent.productivity_score.toFixed(1)}
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-center">
                          {agent.sla_compliant ? (
                            <CheckCircle className="h-5 w-5 text-green-600 mx-auto" />
                          ) : (
                            <XCircle className="h-5 w-5 text-red-600 mx-auto" />
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Call Distribution */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">📊 Distribución de Llamadas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Contestadas</span>
                      <span className="font-semibold text-green-600">
                        {performanceData.overall.total_answered} ({performanceData.overall.overall_answer_rate}%)
                      </span>
                    </div>
                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-green-500"
                        style={{ width: `${performanceData.overall.overall_answer_rate}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Fallidas</span>
                      <span className="font-semibold text-red-600">
                        {performanceData.overall.total_failed} ({(100 - performanceData.overall.overall_answer_rate).toFixed(2)}%)
                      </span>
                    </div>
                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-red-500"
                        style={{ width: `${100 - performanceData.overall.overall_answer_rate}%` }}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">⚙️ Factores de Productividad</CardTitle>
              </CardHeader>
              <CardContent className="text-sm">
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span>Answer Rate (40%)</span>
                    <span className="font-semibold">{performanceData.overall.overall_answer_rate}%</span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span>Eficiencia Tiempo (30%)</span>
                    <span className="font-semibold">{Math.round(performanceData.overall.avg_handle_time)}s</span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span>Volumen (30%)</span>
                    <span className="font-semibold">{performanceData.overall.total_calls} llamadas</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
