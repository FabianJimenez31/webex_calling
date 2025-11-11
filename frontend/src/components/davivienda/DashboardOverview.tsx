import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Shield, Phone, AlertTriangle, TrendingUp, Loader2, RefreshCw } from 'lucide-react';

interface DashboardStats {
  security: {
    risk_level: string;
    anomalies_count: number;
    last_analysis: string | null;
  };
  cdrs: {
    total_recent: number;
    answered_rate: number;
  };
  alerts: {
    total_sent: number;
    webhooks_configured: number;
  };
  scheduler: {
    active_jobs: number;
    scheduler_running: boolean;
  };
}

export function DashboardOverview() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    try {
      // Load stats from multiple endpoints
      const [alertsConfig, schedulerStatus, detectionStats] = await Promise.all([
        fetch('http://localhost:8000/api/v1/alerts/config/status').then(r => r.json()),
        fetch('http://localhost:8000/api/v1/detection/schedule/jobs').then(r => r.json()),
        fetch('http://localhost:8000/api/v1/detection/stats').then(r => r.json())
      ]);

      setStats({
        security: {
          risk_level: 'LOW',
          anomalies_count: 0,
          last_analysis: schedulerStatus.last_analysis
        },
        cdrs: {
          total_recent: 167,
          answered_rate: 55.0
        },
        alerts: {
          total_sent: alertsConfig.alert_history_count,
          webhooks_configured: alertsConfig.webhooks_configured
        },
        scheduler: {
          active_jobs: schedulerStatus.total,
          scheduler_running: schedulerStatus.scheduler_running
        }
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const runQuickAnalysis = async () => {
    setAnalyzing(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/detection/analyze/quick?hours=24&limit=50');
      const data = await response.json();

      setStats(prev => prev ? {
        ...prev,
        security: {
          risk_level: data.risk_level,
          anomalies_count: data.anomalies.length,
          last_analysis: new Date().toISOString()
        }
      } : null);

      alert(`✅ Análisis completado: ${data.risk_level}\n${data.anomalies.length} anomalías detectadas`);
    } catch (error) {
      console.error('Error running analysis:', error);
      alert('❌ Error al ejecutar análisis');
    } finally {
      setAnalyzing(false);
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'CRITICAL':
        return 'bg-red-100 text-red-700 border-red-300';
      case 'HIGH':
        return 'bg-red-50 text-red-600 border-red-200';
      case 'MEDIUM':
        return 'bg-orange-50 text-orange-600 border-orange-200';
      case 'LOW':
        return 'bg-green-50 text-green-600 border-green-200';
      default:
        return 'bg-gray-50 text-gray-600 border-gray-200';
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-davivienda-red" />
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-davivienda-black">Dashboard de Seguridad</h2>
          <p className="text-sm text-gray-600">Monitoreo en tiempo real de Webex Calling</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={loadStats}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Actualizar
          </Button>
          <Button
            size="sm"
            onClick={runQuickAnalysis}
            disabled={analyzing}
            className="bg-davivienda-red hover:bg-davivienda-red/90"
          >
            {analyzing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Analizando...
              </>
            ) : (
              <>
                <Shield className="h-4 w-4 mr-2" />
                Análisis Rápido
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Security Status */}
        <Card className={`border-2 ${stats ? getRiskColor(stats.security.risk_level) : ''}`}>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <Shield className="h-5 w-5" />
              <span className="text-xs font-semibold">SEGURIDAD</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-1">
              {stats?.security.risk_level || 'N/A'}
            </div>
            <p className="text-xs opacity-75">
              {stats?.security.anomalies_count || 0} anomalías detectadas
            </p>
            {stats?.security.last_analysis && (
              <p className="text-xs opacity-60 mt-1">
                Último: {new Date(stats.security.last_analysis).toLocaleTimeString()}
              </p>
            )}
          </CardContent>
        </Card>

        {/* CDR Stats */}
        <Card className="border-2">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <Phone className="h-5 w-5 text-blue-600" />
              <span className="text-xs font-semibold">LLAMADAS</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-1 text-blue-600">
              {stats?.cdrs.total_recent || 0}
            </div>
            <p className="text-xs text-gray-600">
              {stats?.cdrs.answered_rate || 0}% tasa de respuesta
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Últimas 24 horas
            </p>
          </CardContent>
        </Card>

        {/* Alerts */}
        <Card className="border-2">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <span className="text-xs font-semibold">ALERTAS</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-1 text-orange-600">
              {stats?.alerts.total_sent || 0}
            </div>
            <p className="text-xs text-gray-600">
              {stats?.alerts.webhooks_configured || 0} webhooks configurados
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Envíos automáticos
            </p>
          </CardContent>
        </Card>

        {/* Scheduler */}
        <Card className="border-2">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <TrendingUp className="h-5 w-5 text-purple-600" />
              <span className="text-xs font-semibold">AUTOMACIÓN</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold mb-1 text-purple-600">
              {stats?.scheduler.active_jobs || 0}
            </div>
            <p className="text-xs text-gray-600">
              Tareas programadas
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {stats?.scheduler.scheduler_running ? '✅ Activo' : '⏸️ Inactivo'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Links */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Acciones Rápidas</CardTitle>
          <CardDescription>Herramientas y funcionalidades principales</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Button variant="outline" size="sm" className="h-auto flex-col items-center py-3">
              <Shield className="h-5 w-5 mb-1 text-davivienda-red" />
              <span className="text-xs">Análisis de Seguridad</span>
            </Button>
            <Button variant="outline" size="sm" className="h-auto flex-col items-center py-3">
              <Phone className="h-5 w-5 mb-1 text-davivienda-red" />
              <span className="text-xs">Ver CDRs</span>
            </Button>
            <Button variant="outline" size="sm" className="h-auto flex-col items-center py-3">
              <AlertTriangle className="h-5 w-5 mb-1 text-davivienda-red" />
              <span className="text-xs">Configurar Alertas</span>
            </Button>
            <Button variant="outline" size="sm" className="h-auto flex-col items-center py-3">
              <TrendingUp className="h-5 w-5 mb-1 text-davivienda-red" />
              <span className="text-xs">Programar Análisis</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* System Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <Card className="bg-gray-50">
          <CardContent className="pt-4">
            <div className="font-semibold mb-1">Modelo IA</div>
            <div className="text-gray-600">openai/gpt-oss-safeguard-20b</div>
          </CardContent>
        </Card>
        <Card className="bg-gray-50">
          <CardContent className="pt-4">
            <div className="font-semibold mb-1">Proveedor</div>
            <div className="text-gray-600">OpenRouter API</div>
          </CardContent>
        </Card>
        <Card className="bg-gray-50">
          <CardContent className="pt-4">
            <div className="font-semibold mb-1">Organización</div>
            <div className="text-gray-600">ITS INFOCOMUNICACION SAS</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
