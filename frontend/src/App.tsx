/**
 * Webex Calling Security AI
 * Dashboard de Seguridad y Detección de Anomalías
 */
import React, { useState } from 'react';
import { MainDashboard } from './components/davivienda/MainDashboard';
import { WebexAIModule } from './components/davivienda/WebexAIModule';
import { ReportsPanel } from './components/davivienda/ReportsPanel';
import { AlertsPanel } from './components/davivienda/AlertsPanel';
import { SchedulerPanel } from './components/davivienda/SchedulerPanel';
import { SecurityDashboard } from './components/davivienda/SecurityDashboard';
import { AgentPerformanceDashboard } from './components/davivienda/AgentPerformanceDashboard';
import { SLAComplianceView } from './components/davivienda/SLAComplianceView';
import { StaffingRecommendations } from './components/davivienda/StaffingRecommendations';
import { RecordingsManager } from './components/davivienda/RecordingsManager';
import { AuthStatusBanner } from './components/davivienda/AuthStatusBanner';
import {
  LayoutDashboard,
  Sparkles,
  Shield,
  Download,
  Bell,
  Clock,
  Users,
  CheckCircle,
  Calendar,
  FileAudio
} from 'lucide-react';

type TabType = 'dashboard' | 'ai' | 'security' | 'reports' | 'alerts' | 'scheduler' | 'fraud' | 'agents' | 'recordings' | 'sla' | 'staffing';

interface Tab {
  id: TabType;
  label: string;
  icon: React.ReactNode;
  component: React.ReactNode;
}

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');

  const tabs: Tab[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <LayoutDashboard className="h-4 w-4" />,
      component: <MainDashboard />
    },
    {
      id: 'fraud',
      label: 'Seguridad & Fraude',
      icon: <Shield className="h-4 w-4" />,
      component: <SecurityDashboard />
    },
    {
      id: 'agents',
      label: 'Performance Agentes',
      icon: <Users className="h-4 w-4" />,
      component: <AgentPerformanceDashboard />
    },
    {
      id: 'recordings',
      label: 'Grabaciones',
      icon: <FileAudio className="h-4 w-4" />,
      component: <RecordingsManager />
    },
    {
      id: 'sla',
      label: 'SLA Compliance',
      icon: <CheckCircle className="h-4 w-4" />,
      component: <SLAComplianceView />
    },
    {
      id: 'staffing',
      label: 'Staffing',
      icon: <Calendar className="h-4 w-4" />,
      component: <StaffingRecommendations />
    },
    {
      id: 'ai',
      label: 'Módulo IA Webex',
      icon: <Sparkles className="h-4 w-4" />,
      component: <WebexAIModule />
    },
    {
      id: 'reports',
      label: 'Reportes',
      icon: <Download className="h-4 w-4" />,
      component: <ReportsPanel />
    },
    {
      id: 'alerts',
      label: 'Alertas',
      icon: <Bell className="h-4 w-4" />,
      component: <AlertsPanel />
    },
    {
      id: 'scheduler',
      label: 'Programación',
      icon: <Clock className="h-4 w-4" />,
      component: <SchedulerPanel />
    }
  ];

  const activeTabData = tabs.find(tab => tab.id === activeTab);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-davivienda-red rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-davivienda-black">Webex Calling Security</h1>
                <p className="text-xs text-gray-600">AI-Powered Threat Detection • Davivienda</p>
              </div>
            </div>

            {/* User menu */}
            <div className="flex items-center gap-3">
              <div className="text-right mr-2">
                <p className="text-sm font-medium text-davivienda-black">Admin</p>
                <p className="text-xs text-gray-500">ITS INFOCOMUNICACION SAS</p>
              </div>
              <div className="w-10 h-10 bg-davivienda-red rounded-full flex items-center justify-center text-white font-bold">
                A
              </div>
            </div>
          </div>

          {/* Tabs Navigation */}
          <div className="flex gap-1 -mb-px overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-davivienda-red text-davivienda-red font-medium'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                }`}
              >
                {tab.icon}
                <span className="text-sm">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="max-w-7xl mx-auto">
          <AuthStatusBanner />
          {activeTabData?.component}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div>
              © 2025 Davivienda • Webex Calling Security AI
            </div>
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                Sistema Operacional
              </span>
              <span>•</span>
              <span>Powered by ITS Infocom IA Division</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
