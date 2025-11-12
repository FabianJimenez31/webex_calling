import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Bell, Mail, Webhook, Loader2, CheckCircle2, AlertTriangle, History } from 'lucide-react';

interface AlertConfig {
  webhooks_configured: number;
  email_recipients_configured: number;
  alert_history_count: number;
}

interface AlertHistoryItem {
  timestamp: string;
  risk_level: string;
  assessment: string;
  anomalies: any[];
  analyzed_cdrs: number;
}

export function AlertsPanel() {
  const [webhookUrls, setWebhookUrls] = useState('');
  const [emailRecipients, setEmailRecipients] = useState('');
  const [config, setConfig] = useState<AlertConfig | null>(null);
  const [history, setHistory] = useState<AlertHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await fetch('/api/v1/alerts/config/status');
      const data = await response.json();
      setConfig(data);
    } catch (error) {
      console.error('Error loading config:', error);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await fetch('/api/v1/alerts/history?limit=20');
      const data = await response.json();
      setHistory(data.alerts);
      setShowHistory(true);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const configureWebhooks = async () => {
    setLoading(true);
    try {
      const urls = webhookUrls.split('\n').filter(url => url.trim());

      const response = await fetch('/api/v1/alerts/config/webhooks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          webhook_urls: urls
        })
      });

      if (!response.ok) throw new Error('Failed to configure webhooks');

      alert('✅ Webhooks configurados correctamente');
      loadConfig();
    } catch (error) {
      console.error('Error configuring webhooks:', error);
      alert('❌ Error al configurar webhooks');
    } finally {
      setLoading(false);
    }
  };

  const configureEmails = async () => {
    setLoading(true);
    try {
      const emails = emailRecipients.split('\n').filter(email => email.trim());

      const response = await fetch('/api/v1/alerts/config/emails', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email_recipients: emails
        })
      });

      if (!response.ok) throw new Error('Failed to configure emails');

      alert('✅ Destinatarios de email configurados correctamente');
      loadConfig();
    } catch (error) {
      console.error('Error configuring emails:', error);
      alert('❌ Error al configurar emails');
    } finally {
      setLoading(false);
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
                <Bell className="h-5 w-5 text-davivienda-red" />
                Configuración de Alertas
              </CardTitle>
              <CardDescription>
                Configura notificaciones automáticas para anomalías de seguridad
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
          {config && (
            <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
              <div className="text-center">
                <div className="text-2xl font-bold text-davivienda-red">
                  {config.webhooks_configured}
                </div>
                <div className="text-xs text-gray-600">Webhooks</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-davivienda-red">
                  {config.email_recipients_configured}
                </div>
                <div className="text-xs text-gray-600">Emails</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-davivienda-red">
                  {config.alert_history_count}
                </div>
                <div className="text-xs text-gray-600">Alertas enviadas</div>
              </div>
            </div>
          )}

          {/* Webhooks Configuration */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Webhook className="h-4 w-4 text-davivienda-red" />
              <Label className="text-sm font-semibold">Webhooks (Slack/Teams)</Label>
            </div>
            <div className="space-y-2">
              <textarea
                className="w-full p-2 border rounded-md text-sm font-mono"
                rows={3}
                placeholder="https://hooks.slack.com/services/YOUR/WEBHOOK/URL
https://outlook.office.com/webhook/YOUR/WEBHOOK/URL"
                value={webhookUrls}
                onChange={(e) => setWebhookUrls(e.target.value)}
              />
              <p className="text-xs text-gray-500">
                Una URL por línea. Soporta Slack y Microsoft Teams.
              </p>
              <Button
                onClick={configureWebhooks}
                disabled={loading || !webhookUrls.trim()}
                className="bg-davivienda-red hover:bg-davivienda-red/90"
                size="sm"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Configurando...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                    Configurar Webhooks
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Email Configuration */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Mail className="h-4 w-4 text-davivienda-red" />
              <Label className="text-sm font-semibold">Destinatarios de Email</Label>
            </div>
            <div className="space-y-2">
              <textarea
                className="w-full p-2 border rounded-md text-sm font-mono"
                rows={3}
                placeholder="admin@davivienda.com
security@davivienda.com
ops@davivienda.com"
                value={emailRecipients}
                onChange={(e) => setEmailRecipients(e.target.value)}
              />
              <p className="text-xs text-gray-500">
                Un email por línea. (Requiere configuración SMTP)
              </p>
              <Button
                onClick={configureEmails}
                disabled={loading || !emailRecipients.trim()}
                variant="outline"
                size="sm"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Configurando...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                    Configurar Emails
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Info */}
          <div className="text-xs text-gray-500 p-3 bg-blue-50 rounded border border-blue-200">
            <p className="font-medium text-blue-900 mb-1">💡 Información</p>
            <ul className="list-disc list-inside space-y-1 text-blue-800">
              <li>Las alertas se envían automáticamente para riesgo MEDIUM o superior</li>
              <li>Los webhooks funcionan con Slack y Microsoft Teams</li>
              <li>Las alertas incluyen detalles de anomalías detectadas</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* History Modal */}
      {showHistory && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Historial de Alertas</CardTitle>
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
                <AlertTriangle className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p className="text-sm">No hay alertas enviadas aún</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {history.map((alert, idx) => (
                  <div
                    key={idx}
                    className="p-3 border rounded-lg space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${getRiskColor(alert.risk_level)}`}>
                        {alert.risk_level}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(alert.timestamp).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm">{alert.assessment}</p>
                    <div className="text-xs text-gray-600">
                      {alert.anomalies.length} anomalías • {alert.analyzed_cdrs} CDRs analizados
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
