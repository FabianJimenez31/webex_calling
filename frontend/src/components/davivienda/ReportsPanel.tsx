import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Download, FileText, Table, Loader2, Shield, Phone } from 'lucide-react';
import { Input } from '../ui/input';
import { Label } from '../ui/label';

export function ReportsPanel() {
  const [loading, setLoading] = useState<string | null>(null);
  const [hours, setHours] = useState(24);
  const [limit, setLimit] = useState(100);

  const downloadSecurityPDF = async () => {
    setLoading('security-pdf');
    try {
      const response = await fetch(
        `/api/v1/reports/security/pdf?hours=${hours}&limit=${limit}`
      );

      if (!response.ok) throw new Error('Failed to generate report');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `security_report_${new Date().getTime()}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading security PDF:', error);
      alert('Error al generar el reporte. Por favor intenta de nuevo.');
    } finally {
      setLoading(null);
    }
  };

  const downloadSecurityCSV = async () => {
    setLoading('security-csv');
    try {
      const response = await fetch(
        `/api/v1/reports/security/csv?hours=${hours}&limit=${limit}`
      );

      if (!response.ok) throw new Error('Failed to generate report');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `security_analysis_${new Date().getTime()}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading security CSV:', error);
      alert('Error al generar el reporte. Por favor intenta de nuevo.');
    } finally {
      setLoading(null);
    }
  };

  const downloadCDRsCSV = async () => {
    setLoading('cdrs-csv');
    try {
      const response = await fetch(
        `/api/v1/reports/cdrs/csv?hours=${hours}&limit=${limit * 2}`
      );

      if (!response.ok) throw new Error('Failed to generate report');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `cdrs_${new Date().getTime()}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading CDRs CSV:', error);
      alert('Error al exportar CDRs. Por favor intenta de nuevo.');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5 text-davivienda-red" />
            Exportar Reportes
          </CardTitle>
          <CardDescription>
            Descarga reportes profesionales en PDF o exporta datos en CSV
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Configuration */}
          <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="space-y-2">
              <Label htmlFor="hours">Horas de datos</Label>
              <Input
                id="hours"
                type="number"
                min="1"
                max="48"
                value={hours}
                onChange={(e) => setHours(parseInt(e.target.value) || 24)}
              />
              <p className="text-xs text-gray-500">1-48 horas</p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="limit">Máximo de CDRs</Label>
              <Input
                id="limit"
                type="number"
                min="10"
                max="500"
                value={limit}
                onChange={(e) => setLimit(parseInt(e.target.value) || 100)}
              />
              <p className="text-xs text-gray-500">10-500 registros</p>
            </div>
          </div>

          {/* Security Reports */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-davivienda-red" />
              <h3 className="font-semibold text-sm">Análisis de Seguridad</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Card className="border-2">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    <CardTitle className="text-sm">Reporte PDF</CardTitle>
                  </div>
                  <CardDescription className="text-xs">
                    Reporte profesional con análisis completo de seguridad
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    onClick={downloadSecurityPDF}
                    disabled={loading !== null}
                    className="w-full bg-davivienda-red hover:bg-davivienda-red/90"
                    size="sm"
                  >
                    {loading === 'security-pdf' ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Generando...
                      </>
                    ) : (
                      <>
                        <Download className="h-4 w-4 mr-2" />
                        Descargar PDF
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              <Card className="border-2">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <Table className="h-4 w-4" />
                    <CardTitle className="text-sm">Análisis CSV</CardTitle>
                  </div>
                  <CardDescription className="text-xs">
                    Datos estructurados para análisis posterior
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    onClick={downloadSecurityCSV}
                    disabled={loading !== null}
                    variant="outline"
                    className="w-full"
                    size="sm"
                  >
                    {loading === 'security-csv' ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Generando...
                      </>
                    ) : (
                      <>
                        <Download className="h-4 w-4 mr-2" />
                        Descargar CSV
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* CDR Export */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Phone className="h-4 w-4 text-davivienda-red" />
              <h3 className="font-semibold text-sm">Datos de Llamadas (CDRs)</h3>
            </div>

            <Card className="border-2">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Table className="h-4 w-4" />
                  <CardTitle className="text-sm">Exportar CDRs</CardTitle>
                </div>
                <CardDescription className="text-xs">
                  Exporta todos los registros de llamadas en formato CSV
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={downloadCDRsCSV}
                  disabled={loading !== null}
                  variant="outline"
                  className="w-full"
                  size="sm"
                >
                  {loading === 'cdrs-csv' ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Exportando...
                    </>
                  ) : (
                    <>
                      <Download className="h-4 w-4 mr-2" />
                      Exportar CDRs a CSV
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Info */}
          <div className="text-xs text-gray-500 p-3 bg-blue-50 rounded border border-blue-200">
            <p className="font-medium text-blue-900 mb-1">💡 Información</p>
            <ul className="list-disc list-inside space-y-1 text-blue-800">
              <li>Los reportes PDF incluyen tema Davivienda</li>
              <li>Los archivos CSV son compatibles con Excel</li>
              <li>Los datos se obtienen de las últimas {hours} horas</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
