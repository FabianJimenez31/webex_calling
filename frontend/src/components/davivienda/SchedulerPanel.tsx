import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Clock, Play, Square, Loader2, Calendar, History, Zap } from 'lucide-react';

interface ScheduledJob {
  id: string;
  name: string;
  next_run: string | null;
  trigger: string;
}

interface SchedulerStatus {
  total: number;
  scheduler_running: boolean;
  last_analysis: string | null;
  jobs: ScheduledJob[];
}

interface AnalysisHistory {
  timestamp: string;
  cdrs_analyzed: number;
  risk_level: string;
  anomalies_count: number;
  overall_assessment: string;
}

export function SchedulerPanel() {
  const [status, setStatus] = useState<SchedulerStatus | null>(null);
  const [history, setHistory] = useState<AnalysisHistory[]>([]);
  const [loading, setLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  // Config for new schedule
  const [scheduleType, setScheduleType] = useState<'hourly' | 'daily' | 'custom'>('hourly');
  const [hours, setHours] = useState(1);
  const [limit, setLimit] = useState(100);
  const [dailyHour, setDailyHour] = useState(8);
  const [dailyMinute, setDailyMinute] = useState(0);
  const [customInterval, setCustomInterval] = useState(30);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const response = await fetch('/api/v1/detection/schedule/jobs');
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Error loading scheduler status:', error);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await fetch('/api/v1/detection/schedule/history?limit=20');
      const data = await response.json();
      setHistory(data.analyses);
      setShowHistory(true);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const enableSchedule = async () => {
    setLoading(true);
    try {
      const config: any = {
        schedule_type: scheduleType,
        hours,
        limit,
      };

      if (scheduleType === 'daily') {
        config.hour = dailyHour;
        config.minute = dailyMinute;
      } else if (scheduleType === 'custom') {
        config.interval_minutes = customInterval;
      }

      const response = await fetch('/api/v1/detection/schedule/enable', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
      });

      if (!response.ok) throw new Error('Failed to enable schedule');

      const data = await response.json();
      alert(`✅ Análisis programado configurado: ${data.job_name}`);
      loadStatus();
    } catch (error) {
      console.error('Error enabling schedule:', error);
      alert('❌ Error al configurar análisis programado');
    } finally {
      setLoading(false);
    }
  };

  const disableJob = async (jobId: string) => {
    try {
      const response = await fetch(`/api/v1/detection/schedule/disable/${jobId}`, {
        method: 'POST',
      });

      if (!response.ok) throw new Error('Failed to disable job');

      alert('✅ Tarea programada deshabilitada');
      loadStatus();
    } catch (error) {
      console.error('Error disabling job:', error);
      alert('❌ Error al deshabilitar tarea');
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'CRITICAL':
        return 'text-red-700 bg-red-100';
      case 'HIGH':
        return 'text-red-600 bg-red-50';
      case 'MEDIUM':
        return 'text-orange-600 bg-orange-50';
      case 'LOW':
        return 'text-green-600 bg-green-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-davivienda-red" />
                Análisis Programado
              </CardTitle>
              <CardDescription>
                Configura análisis automáticos de seguridad
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadHistory}
            >
              <History className="h-4 w-4 mr-2" />
              Ver historial
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Status */}
          {status && (
            <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
              <div className="text-center">
                <div className={`text-2xl font-bold ${status.scheduler_running ? 'text-green-600' : 'text-gray-400'}`}>
                  {status.scheduler_running ? 'ACTIVO' : 'INACTIVO'}
                </div>
                <div className="text-xs text-gray-600">Estado</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-davivienda-red">
                  {status.total}
                </div>
                <div className="text-xs text-gray-600">Tareas</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-davivienda-red">
                  {status.last_analysis ? new Date(status.last_analysis).toLocaleTimeString() : '-'}
                </div>
                <div className="text-xs text-gray-600">Último análisis</div>
              </div>
            </div>
          )}

          {/* Active Jobs */}
          {status && status.jobs.length > 0 && (
            <div className="space-y-3">
              <Label className="text-sm font-semibold">Tareas Activas</Label>
              <div className="space-y-2">
                {status.jobs.map((job) => (
                  <div
                    key={job.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex-1">
                      <div className="font-medium text-sm">{job.name}</div>
                      <div className="text-xs text-gray-500">
                        Próxima ejecución: {job.next_run ? new Date(job.next_run).toLocaleString() : 'N/A'}
                      </div>
                    </div>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => disableJob(job.id)}
                    >
                      <Square className="h-3 w-3 mr-1" />
                      Detener
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* New Schedule Configuration */}
          <div className="space-y-4 p-4 border-2 border-dashed rounded-lg">
            <Label className="text-sm font-semibold">Configurar Nueva Programación</Label>

            {/* Schedule Type */}
            <div className="space-y-2">
              <Label className="text-xs">Tipo de Programación</Label>
              <div className="grid grid-cols-3 gap-2">
                <Button
                  variant={scheduleType === 'hourly' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setScheduleType('hourly')}
                  className={scheduleType === 'hourly' ? 'bg-davivienda-red' : ''}
                >
                  <Clock className="h-3 w-3 mr-1" />
                  Horario
                </Button>
                <Button
                  variant={scheduleType === 'daily' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setScheduleType('daily')}
                  className={scheduleType === 'daily' ? 'bg-davivienda-red' : ''}
                >
                  <Calendar className="h-3 w-3 mr-1" />
                  Diario
                </Button>
                <Button
                  variant={scheduleType === 'custom' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setScheduleType('custom')}
                  className={scheduleType === 'custom' ? 'bg-davivienda-red' : ''}
                >
                  <Zap className="h-3 w-3 mr-1" />
                  Personalizado
                </Button>
              </div>
            </div>

            {/* Daily Configuration */}
            {scheduleType === 'daily' && (
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label className="text-xs">Hora (UTC)</Label>
                  <Input
                    type="number"
                    min="0"
                    max="23"
                    value={dailyHour}
                    onChange={(e) => setDailyHour(parseInt(e.target.value) || 0)}
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Minuto</Label>
                  <Input
                    type="number"
                    min="0"
                    max="59"
                    value={dailyMinute}
                    onChange={(e) => setDailyMinute(parseInt(e.target.value) || 0)}
                  />
                </div>
              </div>
            )}

            {/* Custom Interval */}
            {scheduleType === 'custom' && (
              <div className="space-y-1">
                <Label className="text-xs">Intervalo (minutos)</Label>
                <Input
                  type="number"
                  min="5"
                  max="1440"
                  value={customInterval}
                  onChange={(e) => setCustomInterval(parseInt(e.target.value) || 30)}
                />
                <p className="text-xs text-gray-500">Cada {customInterval} minutos</p>
              </div>
            )}

            {/* Common Configuration */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-xs">Horas de datos</Label>
                <Input
                  type="number"
                  min="1"
                  max="48"
                  value={hours}
                  onChange={(e) => setHours(parseInt(e.target.value) || 1)}
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Máx. CDRs</Label>
                <Input
                  type="number"
                  min="10"
                  max="500"
                  value={limit}
                  onChange={(e) => setLimit(parseInt(e.target.value) || 100)}
                />
              </div>
            </div>

            <Button
              onClick={enableSchedule}
              disabled={loading}
              className="w-full bg-davivienda-red hover:bg-davivienda-red/90"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Configurando...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Activar Programación
                </>
              )}
            </Button>
          </div>

          {/* Info */}
          <div className="text-xs text-gray-500 p-3 bg-blue-50 rounded border border-blue-200">
            <p className="font-medium text-blue-900 mb-1">💡 Información</p>
            <ul className="list-disc list-inside space-y-1 text-blue-800">
              <li>Los análisis se ejecutan automáticamente según la programación</li>
              <li>Se envían alertas si se detectan anomalías (MEDIUM+)</li>
              <li>El historial guarda las últimas 100 ejecuciones</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* History */}
      {showHistory && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Historial de Análisis</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowHistory(false)}
              >
                Cerrar
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {history.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Clock className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p className="text-sm">No hay análisis ejecutados aún</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {history.map((analysis, idx) => (
                  <div
                    key={idx}
                    className="p-3 border rounded-lg space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${getRiskColor(analysis.risk_level)}`}>
                        {analysis.risk_level}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(analysis.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-xs text-gray-600">{analysis.overall_assessment}</p>
                    <div className="text-xs text-gray-500">
                      {analysis.anomalies_count} anomalías • {analysis.cdrs_analyzed} CDRs
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
