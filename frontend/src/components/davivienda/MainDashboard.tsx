import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import {
  Shield,
  Phone,
  Users,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  Loader2,
  RefreshCw,
  Activity,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

interface DashboardData {
  security: {
    score: number;
    risk_level: string;
    total_alerts: number;
    critical_alerts: number;
  };
  performance: {
    total_agents: number;
    total_calls: number;
    answer_rate: number;
    avg_handle_time: number;
    avg_productivity: number;
  };
  sla: {
    overall_score: number;
    status: string;
  };
  recent_activity: any[];
  call_trends: any[];
  agent_comparison: any[];
}

export function MainDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load dashboard summary
      const response = await fetch('http://localhost:8000/api/v1/analytics/dashboard/summary?hours=24');
      const summaryData = await response.json();

      // Transform data for charts
      const transformedData: DashboardData = {
        security: summaryData.security,
        performance: summaryData.performance,
        sla: summaryData.sla,
        recent_activity: summaryData.security.top_alerts || [],
        call_trends: generateCallTrends(), // Mock data for now
        agent_comparison: summaryData.performance.top_performers?.slice(0, 5) || []
      };

      setData(transformedData);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateCallTrends = () => {
    // Generate hourly data for the last 24 hours
    const hours = [];
    for (let i = 23; i >= 0; i--) {
      const hour = new Date();
      hour.setHours(hour.getHours() - i);
      hours.push({
        hour: hour.getHours() + ':00',
        calls: Math.floor(Math.random() * 20) + 5,
        answered: Math.floor(Math.random() * 15) + 3
      });
    }
    return hours;
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    if (score >= 40) return 'bg-orange-100';
    return 'bg-red-100';
  };

  const COLORS = ['#EC0000', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'];

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-davivienda-red" />
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-davivienda-black">Dashboard Principal</h2>
          <p className="text-sm text-gray-600 mt-1">Vista general del sistema - Últimas 24 horas</p>
        </div>
        <Button
          size="sm"
          onClick={loadDashboardData}
          disabled={loading}
          className="bg-davivienda-red hover:bg-davivienda-red/90"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Actualizando...
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4 mr-2" />
              Actualizar
            </>
          )}
        </Button>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Security Score */}
        <Card className={`border-2 ${data.security.score >= 80 ? 'border-green-300' : data.security.score >= 60 ? 'border-yellow-300' : 'border-red-300'}`}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Score de Seguridad</CardTitle>
            <Shield className={`h-4 w-4 ${getScoreColor(data.security.score)}`} />
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold ${getScoreColor(data.security.score)}`}>
              {data.security.score}
            </div>
            <p className="text-xs text-gray-600 mt-1">
              {data.security.total_alerts} alertas detectadas
            </p>
            <div className="flex items-center gap-1 text-xs mt-2">
              {data.security.risk_level === 'BAJO' || data.security.risk_level === 'SEGURO' ? (
                <TrendingUp className="h-3 w-3 text-green-600" />
              ) : (
                <TrendingDown className="h-3 w-3 text-red-600" />
              )}
              <span className="text-gray-600">Nivel: {data.security.risk_level}</span>
            </div>
          </CardContent>
        </Card>

        {/* Total Calls */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Llamadas Totales</CardTitle>
            <Phone className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {data.performance.total_calls}
            </div>
            <p className="text-xs text-gray-600 mt-1">
              {data.performance.answer_rate.toFixed(1)}% contestadas
            </p>
            <div className="flex items-center gap-1 text-xs mt-2">
              <ArrowUpRight className="h-3 w-3 text-blue-600" />
              <span className="text-gray-600">Últimas 24h</span>
            </div>
          </CardContent>
        </Card>

        {/* Active Agents */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Agentes Activos</CardTitle>
            <Users className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">
              {data.performance.total_agents}
            </div>
            <p className="text-xs text-gray-600 mt-1">
              Score promedio: {data.performance.avg_productivity.toFixed(1)}
            </p>
            <div className="flex items-center gap-1 text-xs mt-2">
              <Activity className="h-3 w-3 text-purple-600" />
              <span className="text-gray-600">En servicio</span>
            </div>
          </CardContent>
        </Card>

        {/* SLA Compliance */}
        <Card className={`border-2 ${data.sla.overall_score >= 80 ? 'border-green-300' : 'border-yellow-300'}`}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Cumplimiento SLA</CardTitle>
            {data.sla.overall_score >= 80 ? (
              <CheckCircle className="h-4 w-4 text-green-600" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
            )}
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold ${getScoreColor(data.sla.overall_score)}`}>
              {data.sla.overall_score}%
            </div>
            <p className="text-xs text-gray-600 mt-1">
              {data.sla.status}
            </p>
            <div className="flex items-center gap-1 text-xs mt-2">
              <Clock className="h-3 w-3 text-gray-600" />
              <span className="text-gray-600">Target: 80%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Call Trends Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Tendencia de Llamadas</CardTitle>
            <CardDescription>Volumen de llamadas por hora (últimas 24h)</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.call_trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="hour"
                  stroke="#888888"
                  fontSize={12}
                  tickLine={false}
                />
                <YAxis
                  stroke="#888888"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    background: 'white',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px'
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="calls"
                  stroke="#EC0000"
                  strokeWidth={2}
                  dot={{ fill: '#EC0000', r: 4 }}
                  activeDot={{ r: 6 }}
                  name="Total"
                />
                <Line
                  type="monotone"
                  dataKey="answered"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={{ fill: '#10b981', r: 4 }}
                  name="Contestadas"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Agent Performance Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Top 5 Agentes</CardTitle>
            <CardDescription>Comparación de productividad</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.agent_comparison}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="agent"
                  stroke="#888888"
                  fontSize={12}
                  tickLine={false}
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis
                  stroke="#888888"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    background: 'white',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px'
                  }}
                />
                <Bar
                  dataKey="productivity_score"
                  fill="#EC0000"
                  radius={[8, 8, 0, 0]}
                  name="Productividad"
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity & Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Recent Alerts */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Alertas Recientes</CardTitle>
            <CardDescription>Últimas alertas de seguridad detectadas</CardDescription>
          </CardHeader>
          <CardContent>
            {data.recent_activity.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <CheckCircle className="h-12 w-12 mx-auto mb-3 text-green-500" />
                <p className="font-semibold">✅ Sin alertas recientes</p>
                <p className="text-sm">El sistema está operando normalmente</p>
              </div>
            ) : (
              <div className="space-y-3">
                {data.recent_activity.map((alert: any, idx: number) => (
                  <div
                    key={idx}
                    className={`flex items-start gap-3 p-3 rounded-lg border-l-4 ${
                      alert.severity === 'critical' ? 'bg-red-50 border-l-red-500' :
                      alert.severity === 'high' ? 'bg-orange-50 border-l-orange-500' :
                      'bg-yellow-50 border-l-yellow-500'
                    }`}
                  >
                    <AlertTriangle className={`h-5 w-5 mt-0.5 ${
                      alert.severity === 'critical' ? 'text-red-600' :
                      alert.severity === 'high' ? 'text-orange-600' :
                      'text-yellow-600'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                          alert.severity === 'critical' ? 'bg-red-200 text-red-800' :
                          alert.severity === 'high' ? 'bg-orange-200 text-orange-800' :
                          'bg-yellow-200 text-yellow-800'
                        }`}>
                          {alert.severity?.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">{alert.user}</span>
                      </div>
                      <p className="text-sm font-medium text-gray-900 truncate">{alert.title}</p>
                      <p className="text-xs text-gray-600 mt-1">{alert.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Performance Metrics */}
        <Card>
          <CardHeader>
            <CardTitle>Métricas Clave</CardTitle>
            <CardDescription>Indicadores de performance</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Answer Rate</span>
                <span className="font-semibold">{data.performance.answer_rate.toFixed(1)}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${data.performance.answer_rate >= 80 ? 'bg-green-500' : 'bg-yellow-500'}`}
                  style={{ width: `${data.performance.answer_rate}%` }}
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Avg Handle Time</span>
                <span className="font-semibold">{Math.round(data.performance.avg_handle_time)}s</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${data.performance.avg_handle_time <= 180 ? 'bg-green-500' : 'bg-red-500'}`}
                  style={{ width: `${Math.min((data.performance.avg_handle_time / 180) * 100, 100)}%` }}
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Productividad</span>
                <span className="font-semibold">{data.performance.avg_productivity.toFixed(1)}</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-purple-500"
                  style={{ width: `${data.performance.avg_productivity}%` }}
                />
              </div>
            </div>

            <div className="pt-4 border-t">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-600">Estado General</span>
                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                  data.security.score >= 80 && data.sla.overall_score >= 80
                    ? 'bg-green-100 text-green-700'
                    : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {data.security.score >= 80 && data.sla.overall_score >= 80 ? '✅ SALUDABLE' : '⚠️ ATENCIÓN'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Acceso Rápido</CardTitle>
          <CardDescription>Navegación directa a dashboards especializados</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Button
              variant="outline"
              className="h-20 flex-col gap-2"
              onClick={() => window.location.hash = '#fraud'}
            >
              <Shield className="h-6 w-6 text-davivienda-red" />
              <span className="text-sm">Seguridad & Fraude</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col gap-2"
              onClick={() => window.location.hash = '#agents'}
            >
              <Users className="h-6 w-6 text-davivienda-red" />
              <span className="text-sm">Performance Agentes</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col gap-2"
              onClick={() => window.location.hash = '#sla'}
            >
              <CheckCircle className="h-6 w-6 text-davivienda-red" />
              <span className="text-sm">SLA Compliance</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col gap-2"
              onClick={() => window.location.hash = '#staffing'}
            >
              <Clock className="h-6 w-6 text-davivienda-red" />
              <span className="text-sm">Staffing</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
