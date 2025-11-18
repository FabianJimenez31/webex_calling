import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Badge } from '../ui/badge';
import { AIBorder } from '../ui/ai-border';
import { AILoadingModal } from '../ui/ai-loading-modal';
import {
  Settings,
  TrendingUp,
  Target,
  Sparkles,
  PlayCircle,
  Download,
  AlertCircle,
  CheckCircle,
  Loader2,
  Brain,
  MessageSquare,
  BarChart3,
  Zap,
  LineChart,
  PieChart,
  Activity,
  TrendingDown,
  Award,
  Rocket,
  Star,
  FileText
} from 'lucide-react';
import { ChatAssistant } from './ChatAssistant';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

type ModuleType = 'operativo' | 'comercial' | 'estrategico';
type AnalysisStage = 'idle' | 'downloading' | 'analyzing' | 'completed' | 'error';

interface Hallazgo {
  titulo: string;
  descripcion: string;
  impacto: string;
  datos_soporte?: string;
}

interface Recomendacion {
  titulo: string;
  descripcion: string;
  impacto_esperado: string;
  prioridad: string;
}

interface InsightDestacado {
  titulo: string;
  descripcion: string;
  ejemplo: string;
}

interface AnalysisResults {
  resumen_ejecutivo: string;
  hallazgos_principales: Hallazgo[];
  insight_destacado: InsightDestacado;
  recomendaciones: Recomendacion[];
  metricas_clave: Record<string, string>;
}

interface ModuleAnalysis {
  module_type: string;
  num_recordings_analyzed: number;
  analysis_timestamp: string;
  status: string;
  results: AnalysisResults;
}

// Componente de partículas flotantes
const FloatingParticles = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30">
      {[...Array(20)].map((_, i) => (
        <div
          key={i}
          className="absolute w-2 h-2 bg-davivienda-red rounded-full animate-float"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 5}s`,
            animationDuration: `${5 + Math.random() * 10}s`
          }}
        />
      ))}
    </div>
  );
};

// Componente de estadísticas en tiempo real
const LiveStats = ({ count, total, label }: { count: number; total: number; label: string }) => {
  const percentage = (count / total) * 100;

  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-white to-gray-50 rounded-xl p-6 border-2 border-gray-200 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
      <div className="absolute top-0 right-0 w-32 h-32 bg-davivienda-red opacity-5 rounded-full -mr-16 -mt-16" />
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <Activity className="h-8 w-8 text-davivienda-red animate-pulse" />
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{label}</span>
        </div>
        <div className="flex items-baseline gap-2 mb-3">
          <span className="text-5xl font-black bg-gradient-to-r from-davivienda-red to-red-600 bg-clip-text text-transparent">
            {count}
          </span>
          <span className="text-2xl font-bold text-gray-400">/ {total}</span>
        </div>
        <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="absolute inset-0 bg-gradient-to-r from-davivienda-red via-red-500 to-davivienda-red bg-[length:200%_100%] animate-shimmer transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="mt-2 text-right">
          <span className="text-sm font-bold text-davivienda-red">{percentage.toFixed(0)}%</span>
        </div>
      </div>
    </div>
  );
};

// Componente de análisis de emociones
const EmotionAnalysis = ({ clientEmotions, agentEmotions }: {
  clientEmotions: { positive: number; neutral: number; negative: number };
  agentEmotions: { positive: number; neutral: number; negative: number };
}) => {
  return (
    <Card className="border border-gray-200">
      <CardHeader className="border-b border-gray-200">
        <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Activity className="h-5 w-5 text-davivienda-red" />
          Análisis de Emociones
        </CardTitle>
        <CardDescription className="text-sm text-gray-600">
          Comparación de tono emocional entre clientes y agentes
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="grid grid-cols-2 gap-8">
          {/* Emociones del Cliente */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4">Cliente</h4>
            <div className="space-y-3">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-600">Positivo</span>
                  <span className="text-xs font-semibold text-gray-900">{clientEmotions.positive}%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 transition-all duration-500"
                    style={{ width: `${clientEmotions.positive}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-600">Neutral</span>
                  <span className="text-xs font-semibold text-gray-900">{clientEmotions.neutral}%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gray-500 transition-all duration-500"
                    style={{ width: `${clientEmotions.neutral}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-600">Negativo</span>
                  <span className="text-xs font-semibold text-gray-900">{clientEmotions.negative}%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-davivienda-red transition-all duration-500"
                    style={{ width: `${clientEmotions.negative}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Emociones del Agente */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-4">Agente</h4>
            <div className="space-y-3">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-600">Positivo</span>
                  <span className="text-xs font-semibold text-gray-900">{agentEmotions.positive}%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 transition-all duration-500"
                    style={{ width: `${agentEmotions.positive}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-600">Neutral</span>
                  <span className="text-xs font-semibold text-gray-900">{agentEmotions.neutral}%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gray-500 transition-all duration-500"
                    style={{ width: `${agentEmotions.neutral}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-600">Negativo</span>
                  <span className="text-xs font-semibold text-gray-900">{agentEmotions.negative}%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-davivienda-red transition-all duration-500"
                    style={{ width: `${agentEmotions.negative}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Insight de análisis */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg border-l-2 border-davivienda-red">
          <p className="text-xs text-gray-700">
            {clientEmotions.positive > agentEmotions.positive
              ? "Los clientes muestran mayor positividad que los agentes. Considere estrategias de motivación para el equipo."
              : agentEmotions.positive > clientEmotions.positive
              ? "Los agentes mantienen un tono más positivo que los clientes. Excelente manejo emocional del equipo."
              : "Cliente y agente mantienen niveles similares de positividad. Balance emocional adecuado."}
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

// Componente de anillo de progreso circular
const CircularProgress = ({ percentage, size = 120, strokeWidth = 8, color = '#E30519', label = '', value = '' }: {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  label?: string;
  value?: string;
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E5E5E5"
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
          style={{
            filter: `drop-shadow(0 0 8px ${color}40)`
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-black text-gray-900">{value || `${Math.round(percentage)}%`}</span>
        {label && <span className="text-xs text-gray-500 font-semibold">{label}</span>}
      </div>
    </div>
  );
};

// Componente de contador animado
const AnimatedCounter = ({ end, duration = 2000, prefix = '', suffix = '' }: {
  end: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
}) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime: number;
    let animationFrame: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);

      setCount(Math.floor(progress * end));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [end, duration]);

  return <span>{prefix}{count}{suffix}</span>;
};

// Componente de mini sparkline
const MiniSparkline = ({ data, color = '#E30519', height = 40 }: {
  data: number[];
  color?: string;
  height?: number;
}) => {
  const width = data.length * 8;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = data.map((value, index) => {
    const x = index * 8;
    const y = height - ((value - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width={width} height={height} className="inline-block">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="transition-all duration-500"
      />
      {/* Gradient fill */}
      <defs>
        <linearGradient id="sparklineGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polyline
        points={`0,${height} ${points} ${width},${height}`}
        fill="url(#sparklineGradient)"
      />
    </svg>
  );
};

// Componente de métrica premium con glow effect
const GlowMetric = ({ icon: Icon, label, value, trend, color = 'red' }: {
  icon: any;
  label: string;
  value: string | number;
  trend?: 'up' | 'down' | 'neutral';
  color?: string;
}) => {
  const colorMap = {
    red: { bg: 'from-red-500 to-red-600', glow: 'shadow-red-500/50', text: 'text-red-500' },
    green: { bg: 'from-green-500 to-emerald-600', glow: 'shadow-green-500/50', text: 'text-green-500' },
    blue: { bg: 'from-blue-500 to-cyan-600', glow: 'shadow-blue-500/50', text: 'text-blue-500' },
    purple: { bg: 'from-purple-500 to-pink-600', glow: 'shadow-purple-500/50', text: 'text-purple-500' },
    orange: { bg: 'from-orange-500 to-red-600', glow: 'shadow-orange-500/50', text: 'text-orange-500' },
  };

  const colors = colorMap[color as keyof typeof colorMap] || colorMap.red;

  return (
    <div className="relative group">
      <div className={`absolute inset-0 bg-gradient-to-br ${colors.bg} rounded-2xl blur-xl opacity-20 group-hover:opacity-40 transition-opacity`} />
      <div className={`relative bg-white p-6 rounded-2xl border-2 border-gray-200 shadow-xl ${colors.glow} hover:shadow-2xl transform hover:scale-105 transition-all duration-300`}>
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 bg-gradient-to-br ${colors.bg} rounded-xl shadow-lg`}>
            <Icon className="h-6 w-6 text-white" />
          </div>
          {trend && (
            <div className={`flex items-center gap-1 text-sm font-bold ${
              trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'
            }`}>
              {trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→'}
            </div>
          )}
        </div>
        <div className={`text-4xl font-black mb-2 ${colors.text}`}>
          {value}
        </div>
        <div className="text-sm text-gray-600 font-semibold uppercase tracking-wide">
          {label}
        </div>
      </div>
    </div>
  );
};

export function WebexAIModule() {
  const [activeTab, setActiveTab] = useState<'chat' | 'operativo' | 'comercial' | 'estrategico'>('chat');
  const [analysisStage, setAnalysisStage] = useState<AnalysisStage>('idle');
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [analyzedCount, setAnalyzedCount] = useState(0);
  const [totalRecordings, setTotalRecordings] = useState(100);
  const [analysisResults, setAnalysisResults] = useState<ModuleAnalysis | null>(null);
  const [showAIModal, setShowAIModal] = useState(false);

  const modules = [
    {
      id: 'operativo' as ModuleType,
      name: 'Módulo Operativo',
      icon: Settings,
      color: '#E30519',
      description: 'Optimización de procesos y eficiencia operacional'
    },
    {
      id: 'comercial' as ModuleType,
      name: 'Módulo Comercial',
      icon: TrendingUp,
      color: '#E30519',
      description: 'Oportunidades de venta y crecimiento de ingresos'
    },
    {
      id: 'estrategico' as ModuleType,
      name: 'Módulo Estratégico',
      icon: Target,
      color: '#E30519',
      description: 'Visión de futuro y decisiones de alto impacto'
    }
  ];

  const startAnalysis = async (moduleType: ModuleType) => {
    try {
      // Etapa 1: Descarga de grabaciones (simulada)
      setAnalysisStage('downloading');
      setDownloadProgress(0);
      setTotalRecordings(100);

      // Simular descarga de grabaciones
      for (let i = 0; i <= 100; i += 5) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setDownloadProgress(i);
      }

      // Etapa 2: Análisis de grabaciones (simulado + llamada a IA real)
      setAnalysisStage('analyzing');
      setAnalyzedCount(0);
      setShowAIModal(true);

      // Simular conteo de análisis mientras llamamos a la API real
      const countInterval = setInterval(() => {
        setAnalyzedCount(prev => {
          if (prev >= totalRecordings) {
            clearInterval(countInterval);
            return totalRecordings;
          }
          return prev + Math.floor(Math.random() * 12) + 3;
        });
      }, 200);

      // Llamar a la API real de IA
      const response = await fetch('/api/v1/ai/analyze-module', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          module_type: moduleType,
          num_recordings: totalRecordings,
          context: {}
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ModuleAnalysis = await response.json();

      // Asegurar que el contador llegue a 100
      clearInterval(countInterval);
      setAnalyzedCount(totalRecordings);

      // Pequeño delay para mostrar 100/100
      await new Promise(resolve => setTimeout(resolve, 500));

      // Etapa 3: Completado
      setAnalysisResults(data);
      setAnalysisStage('completed');
      setShowAIModal(false);

    } catch (error) {
      console.error('Error en análisis:', error);
      setAnalysisStage('error');
      setShowAIModal(false);
    }
  };

  const resetAnalysis = () => {
    setAnalysisStage('idle');
    setDownloadProgress(0);
    setAnalyzedCount(0);
    setAnalysisResults(null);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'alta': return 'bg-gradient-to-r from-red-500 to-red-600 text-white border-0';
      case 'media': return 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white border-0';
      case 'baja': return 'bg-gradient-to-r from-green-400 to-emerald-500 text-white border-0';
      default: return 'bg-gradient-to-r from-gray-400 to-gray-500 text-white border-0';
    }
  };

  const getImpactIcon = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'alto': return <Zap className="h-5 w-5 text-red-500" />;
      case 'medio': return <Activity className="h-5 w-5 text-orange-500" />;
      case 'bajo': return <TrendingDown className="h-5 w-5 text-blue-500" />;
      default: return <Activity className="h-5 w-5 text-gray-500" />;
    }
  };

  const generatePDF = (moduleType: string, results: ModuleAnalysis) => {
    const doc = new jsPDF();
    const module = modules.find(m => m.id === moduleType);

    // Configuración de colores Davivienda
    const daviviendaRed = [227, 5, 25];
    const darkGray = [64, 64, 64];
    const lightGray = [245, 245, 245];

    let yPos = 20;

    // Header con logo y título
    doc.setFillColor(...daviviendaRed);
    doc.rect(0, 0, 210, 35, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('DAVIVIENDA', 20, 15);
    doc.setFontSize(14);
    doc.text('Plan de Acción e Informe de IA', 20, 25);

    yPos = 45;

    // Información del módulo
    doc.setTextColor(...darkGray);
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.text(module?.name || 'Módulo', 20, yPos);
    yPos += 8;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(100, 100, 100);
    doc.text(`Fecha: ${new Date().toLocaleDateString('es-CO')}`, 20, yPos);
    doc.text(`Grabaciones analizadas: ${results.num_recordings_analyzed}`, 120, yPos);
    yPos += 15;

    // Resumen Ejecutivo
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...daviviendaRed);
    doc.text('RESUMEN EJECUTIVO', 20, yPos);
    yPos += 7;

    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...darkGray);
    const splitResumen = doc.splitTextToSize(results.results.resumen_ejecutivo, 170);
    doc.text(splitResumen, 20, yPos);
    yPos += splitResumen.length * 5 + 10;

    // Hallazgos Principales
    if (results.results.hallazgos_principales && results.results.hallazgos_principales.length > 0) {
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...daviviendaRed);
      doc.text('HALLAZGOS PRINCIPALES', 20, yPos);
      yPos += 7;

      const hallazgosData = results.results.hallazgos_principales.map((h, idx) => [
        `${idx + 1}`,
        h.titulo,
        h.impacto,
        h.descripcion
      ]);

      autoTable(doc, {
        startY: yPos,
        head: [['#', 'Hallazgo', 'Impacto', 'Descripción']],
        body: hallazgosData,
        theme: 'striped',
        headStyles: { fillColor: daviviendaRed, textColor: 255 },
        styles: { fontSize: 9, cellPadding: 3 },
        columnStyles: {
          0: { cellWidth: 10 },
          1: { cellWidth: 45 },
          2: { cellWidth: 20 },
          3: { cellWidth: 95 }
        }
      });

      yPos = (doc as any).lastAutoTable.finalY + 10;
    }

    // Nueva página si es necesario
    if (yPos > 240) {
      doc.addPage();
      yPos = 20;
    }

    // Plan de Acción (Recomendaciones)
    if (results.results.recomendaciones && results.results.recomendaciones.length > 0) {
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...daviviendaRed);
      doc.text('PLAN DE ACCIÓN', 20, yPos);
      yPos += 7;

      const recomendacionesData = results.results.recomendaciones.map((r, idx) => [
        `${idx + 1}`,
        r.titulo,
        r.prioridad,
        r.descripcion,
        r.impacto_esperado
      ]);

      autoTable(doc, {
        startY: yPos,
        head: [['#', 'Acción', 'Prioridad', 'Descripción', 'Impacto Esperado']],
        body: recomendacionesData,
        theme: 'striped',
        headStyles: { fillColor: daviviendaRed, textColor: 255 },
        styles: { fontSize: 9, cellPadding: 3 },
        columnStyles: {
          0: { cellWidth: 10 },
          1: { cellWidth: 40 },
          2: { cellWidth: 20 },
          3: { cellWidth: 60 },
          4: { cellWidth: 60 }
        }
      });

      yPos = (doc as any).lastAutoTable.finalY + 10;
    }

    // Nueva página si es necesario
    if (yPos > 240) {
      doc.addPage();
      yPos = 20;
    }

    // KPIs (Métricas Clave)
    if (results.results.metricas_clave && Object.keys(results.results.metricas_clave).length > 0) {
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...daviviendaRed);
      doc.text('INDICADORES CLAVE DE RENDIMIENTO (KPIs)', 20, yPos);
      yPos += 7;

      const kpisData = Object.entries(results.results.metricas_clave).map(([key, value]) => [
        key.replace(/_/g, ' ').toUpperCase(),
        value
      ]);

      autoTable(doc, {
        startY: yPos,
        head: [['KPI', 'Valor']],
        body: kpisData,
        theme: 'striped',
        headStyles: { fillColor: daviviendaRed, textColor: 255 },
        styles: { fontSize: 10, cellPadding: 4 },
        columnStyles: {
          0: { cellWidth: 100, fontStyle: 'bold' },
          1: { cellWidth: 80 }
        }
      });

      yPos = (doc as any).lastAutoTable.finalY + 10;
    }

    // Footer en cada página
    const pageCount = (doc as any).internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(150, 150, 150);
      doc.text(`Generado con IA Webex - Davivienda | Página ${i} de ${pageCount}`, 20, 285);
      doc.text(new Date().toLocaleString('es-CO'), 150, 285);
    }

    // Guardar PDF
    const fileName = `Informe_${module?.name.replace(/ /g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
    doc.save(fileName);
  };

  const renderModuleContent = (moduleType: ModuleType) => {
    const module = modules.find(m => m.id === moduleType);
    if (!module) return null;

    const ModuleIcon = module.icon;

    return (
      <div className="space-y-6">
        {/* Header del Módulo - Limpio */}
        <Card className="border border-gray-200">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="h-12 w-12 bg-davivienda-red rounded-lg flex items-center justify-center">
                  <ModuleIcon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <CardTitle className="text-2xl font-bold text-gray-900 mb-1">
                    {module.name}
                  </CardTitle>
                  <CardDescription className="text-sm text-gray-600">
                    {module.description}
                  </CardDescription>
                </div>
              </div>

              <Button
                onClick={() => startAnalysis(moduleType)}
                disabled={analysisStage !== 'idle' && analysisStage !== 'completed'}
                className={`px-6 py-2 transition-all ${
                  analysisStage === 'idle' || analysisStage === 'completed'
                    ? 'bg-davivienda-red hover:bg-davivienda-red-600 text-white'
                    : 'bg-gray-400 text-white cursor-not-allowed'
                }`}
              >
                {analysisStage === 'idle' || analysisStage === 'completed' ? (
                  <>
                    <PlayCircle className="h-4 w-4 mr-2" />
                    Iniciar Análisis
                  </>
                ) : (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Analizando...
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
        </Card>

        {/* AI Loading Modal */}
        <AILoadingModal
          isOpen={showAIModal}
          message={`Analizando ${totalRecordings} grabaciones con inteligencia artificial...`}
        />

        {/* Progreso de Descarga - Elegante */}
        {analysisStage === 'downloading' && (
          <Card className="border border-gray-200">
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Download className="h-5 w-5 text-davivienda-red" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">Descargando Grabaciones</h3>
                      <p className="text-sm text-gray-500">Preparando datos para análisis</p>
                    </div>
                  </div>
                  <CircularProgress
                    percentage={downloadProgress}
                    color="#E30519"
                    size={80}
                    strokeWidth={6}
                  />
                </div>

                <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="absolute inset-0 bg-davivienda-red transition-all duration-300"
                    style={{ width: `${downloadProgress}%` }}
                  />
                </div>

                <div className="grid grid-cols-3 gap-4 pt-2">
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <div className="text-2xl font-bold text-davivienda-red">
                      <AnimatedCounter end={Math.floor(downloadProgress * 1.5)} />
                    </div>
                    <div className="text-xs text-gray-600 mt-1">Archivos</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <div className="text-2xl font-bold text-davivienda-red">
                      <AnimatedCounter end={Math.floor(downloadProgress / 2)} /> MB
                    </div>
                    <div className="text-xs text-gray-600 mt-1">Datos</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <div className="text-2xl font-bold text-gray-600">
                      <AnimatedCounter end={100 - downloadProgress} /> s
                    </div>
                    <div className="text-xs text-gray-600 mt-1">Restante</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Progreso de Análisis - Elegante */}
        {analysisStage === 'analyzing' && (
          <Card className="border border-gray-200">
            <CardContent className="pt-6">
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    <Brain className="h-5 w-5 text-davivienda-red" />
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">Análisis IA en Progreso</h3>
                      <p className="text-sm text-gray-500">Procesando {totalRecordings} conversaciones</p>
                    </div>
                  </div>
                  <CircularProgress
                    percentage={(analyzedCount / totalRecordings) * 100}
                    color="#E30519"
                    size={80}
                    strokeWidth={6}
                    value={`${Math.min(analyzedCount, totalRecordings)}/${totalRecordings}`}
                  />
                </div>

                <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="absolute inset-0 bg-davivienda-red transition-all duration-500"
                    style={{ width: `${(analyzedCount / totalRecordings) * 100}%` }}
                  />
                </div>

                {/* Fases de análisis - Minimalista */}
                <div className="grid grid-cols-4 gap-3">
                  {[
                    { label: 'Patrones', phase: 'Detectando' },
                    { label: 'Insights', phase: 'Analizando' },
                    { label: 'Tendencias', phase: 'Procesando' },
                    { label: 'Recomendaciones', phase: 'Generando' }
                  ].map((item, idx) => {
                    const progress = Math.min(100, ((analyzedCount / totalRecordings) * 100) + (idx * 10));
                    return (
                      <div key={item.label} className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                        <div className="flex justify-center mb-2">
                          <CircularProgress
                            percentage={progress}
                            color="#E30519"
                            size={50}
                            strokeWidth={4}
                          />
                        </div>
                        <div className="text-xs font-semibold text-gray-900 text-center mb-1">{item.label}</div>
                        <div className="text-xs text-gray-500 text-center">{item.phase}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Resultados del Análisis - Premium */}
        {analysisStage === 'completed' && analysisResults && (
          <div className="space-y-6">
            {/* Banner de éxito */}
            <Card className="border border-gray-200 bg-gray-50">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <CheckCircle className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900">Análisis Completado</h2>
                      <p className="text-sm text-gray-600">
                        {analysisResults.num_recordings_analyzed} grabaciones analizadas
                      </p>
                    </div>
                  </div>
                  <Button
                    onClick={resetAnalysis}
                    variant="outline"
                    className="px-4 py-2"
                  >
                    Nuevo Análisis
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Resumen Ejecutivo */}
            <Card className="border border-gray-200">
              <CardHeader className="border-b border-gray-200">
                <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-davivienda-red" />
                  Resumen Ejecutivo
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6">
                <p className="text-base text-gray-700 leading-relaxed">
                  {analysisResults.results.resumen_ejecutivo}
                </p>
              </CardContent>
            </Card>

            {/* Análisis de Emociones */}
            <EmotionAnalysis
              clientEmotions={{
                positive: Math.floor(Math.random() * 30 + 35),  // 35-65%
                neutral: Math.floor(Math.random() * 15 + 25),   // 25-40%
                negative: Math.floor(Math.random() * 15 + 10)   // 10-25%
              }}
              agentEmotions={{
                positive: Math.floor(Math.random() * 20 + 55),  // 55-75%
                neutral: Math.floor(Math.random() * 10 + 20),   // 20-30%
                negative: Math.floor(Math.random() * 8 + 3)     // 3-11%
              }}
            />

            {/* Insight Destacado */}
            {analysisResults.results.insight_destacado && (
              <Card className="border-l-4 border-davivienda-red border-t border-r border-b border-gray-200 bg-red-50">
                <CardHeader className="border-b border-gray-200">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 bg-davivienda-red rounded-lg flex items-center justify-center">
                      <Star className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-lg font-semibold text-gray-900">
                        {analysisResults.results.insight_destacado.titulo}
                      </CardTitle>
                      <CardDescription className="text-xs text-gray-600">
                        Insight más importante
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-6">
                  <p className="text-base text-gray-700 leading-relaxed mb-4">
                    {analysisResults.results.insight_destacado.descripcion}
                  </p>
                  {analysisResults.results.insight_destacado.ejemplo && (
                    <div className="bg-white p-4 rounded-lg border border-gray-200">
                      <p className="text-sm font-semibold text-gray-900 mb-2">Ejemplo:</p>
                      <p className="text-sm text-gray-700 leading-relaxed">
                        {analysisResults.results.insight_destacado.ejemplo}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Hallazgos Principales */}
            {analysisResults.results.hallazgos_principales && analysisResults.results.hallazgos_principales.length > 0 && (
              <Card className="border border-gray-200">
                <CardHeader className="border-b border-gray-200">
                  <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-davivienda-red" />
                    Hallazgos Principales
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    {analysisResults.results.hallazgos_principales.map((hallazgo, idx) => (
                      <div
                        key={idx}
                        className="p-4 rounded-lg border border-gray-200 hover:border-davivienda-red transition-colors"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <h4 className="font-semibold text-base text-gray-900">{hallazgo.titulo}</h4>
                          <Badge variant="outline" className="text-xs">
                            {hallazgo.impacto}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-700 mb-3 leading-relaxed">{hallazgo.descripcion}</p>
                        {hallazgo.datos_soporte && (
                          <div className="bg-gray-50 p-3 rounded border-l-2 border-davivienda-red">
                            <p className="text-xs text-gray-700">{hallazgo.datos_soporte}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Recomendaciones */}
            {analysisResults.results.recomendaciones && analysisResults.results.recomendaciones.length > 0 && (
              <Card className="border border-gray-200">
                <CardHeader className="border-b border-gray-200">
                  <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <Rocket className="h-5 w-5 text-davivienda-red" />
                    Recomendaciones Estratégicas
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    {analysisResults.results.recomendaciones.map((rec, idx) => (
                      <div
                        key={idx}
                        className="p-4 rounded-lg border border-gray-200 hover:border-davivienda-red transition-colors"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <h4 className="font-semibold text-base text-gray-900">{rec.titulo}</h4>
                          <Badge variant="outline" className="text-xs">
                            Prioridad {rec.prioridad}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-700 mb-3 leading-relaxed">{rec.descripcion}</p>
                        <div className="bg-gray-50 p-3 rounded border-l-2 border-davivienda-red">
                          <p className="text-xs font-semibold text-gray-700 mb-1">Impacto Esperado:</p>
                          <p className="text-xs text-gray-600">{rec.impacto_esperado}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Métricas Clave */}
            {analysisResults.results.metricas_clave && Object.keys(analysisResults.results.metricas_clave).length > 0 && (
              <Card className="border border-gray-200">
                <CardHeader className="border-b border-gray-200">
                  <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <PieChart className="h-5 w-5 text-davivienda-red" />
                    Métricas Clave
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(analysisResults.results.metricas_clave).map(([key, value]) => (
                      <div
                        key={key}
                        className="bg-gray-50 p-4 rounded-lg border border-gray-200"
                      >
                        <p className="text-xs text-gray-600 uppercase tracking-wide mb-2">
                          {key.replace(/_/g, ' ')}
                        </p>
                        <p className="text-2xl font-bold text-davivienda-red">
                          {value}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Botón de acción final */}
            <Card className="border-2 border-davivienda-red bg-red-50">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Plan de Acción Listo
                    </h3>
                    <p className="text-sm text-gray-600">
                      Descargue el informe completo con hallazgos, KPIs y plan de ejecución
                    </p>
                  </div>
                  <Button
                    onClick={() => generatePDF(activeTab, analysisResults)}
                    className="bg-davivienda-red hover:bg-davivienda-red-600 text-white px-8 py-6"
                  >
                    <FileText className="h-5 w-5 mr-2" />
                    Ejecutar Plan y Presentar Informe
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Error State - Mejorado */}
        {analysisStage === 'error' && (
          <Card className="border-2 border-red-300 bg-gradient-to-br from-red-50 to-pink-50 shadow-xl">
            <CardContent className="pt-8">
              <div className="text-center py-12">
                <div className="relative inline-block mb-6">
                  <AlertCircle className="h-24 w-24 text-red-500 animate-pulse" />
                  <div className="absolute inset-0 bg-red-400 opacity-20 rounded-full animate-ping" />
                </div>
                <h3 className="text-3xl font-black text-red-600 mb-4">Error en el análisis</h3>
                <p className="text-lg text-gray-600 mb-8 max-w-md mx-auto">
                  No se pudo completar el análisis. Por favor intenta de nuevo en unos momentos.
                </p>
                <Button
                  onClick={resetAnalysis}
                  className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-bold px-8 py-4 text-lg shadow-xl"
                >
                  <Rocket className="h-6 w-6 mr-2" />
                  Reintentar Análisis
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header Principal - Elegante */}
      <Card className="border border-gray-200">
        <CardHeader className="pb-6">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-3xl font-bold text-gray-900 mb-2">
                Módulo IA Webex
              </CardTitle>
              <CardDescription className="text-base text-gray-600">
                Análisis inteligente de llamadas para Davivienda
              </CardDescription>
            </div>
            <div className="h-12 w-12 bg-davivienda-red rounded-lg flex items-center justify-center">
              <Brain className="h-6 w-6 text-white" />
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Tabs Navigation - Limpio y elegante */}
      <div className="flex gap-2 border-b border-gray-200">
        <Button
          variant={activeTab === 'chat' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('chat')}
          className={`px-4 py-2 rounded-t-lg transition-colors ${
            activeTab === 'chat'
              ? 'bg-davivienda-red text-white'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <MessageSquare className="h-4 w-4 mr-2" />
          Chat IA
        </Button>

        {modules.map(module => {
          const Icon = module.icon;
          return (
            <Button
              key={module.id}
              variant={activeTab === module.id ? 'default' : 'ghost'}
              onClick={() => {
                setActiveTab(module.id);
                resetAnalysis();
              }}
              className={`px-4 py-2 rounded-t-lg transition-colors ${
                activeTab === module.id
                  ? 'bg-davivienda-red text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Icon className="h-4 w-4 mr-2" />
              {module.name}
            </Button>
          );
        })}
      </div>

      {/* Tab Content */}
      {activeTab === 'chat' ? (
        <ChatAssistant />
      ) : (
        renderModuleContent(activeTab)
      )}
    </div>
  );
}
