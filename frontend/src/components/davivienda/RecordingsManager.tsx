import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { AIBorder } from '../ui/ai-border';
import { AILoadingModal } from '../ui/ai-loading-modal';
import { AudioPlayer } from './AudioPlayer';
import {
  Mic,
  FileAudio,
  MessageSquare,
  Brain,
  TrendingUp,
  CheckCircle2,
  Clock,
  Search,
  Filter,
  Download,
  Loader2,
  ChevronDown,
  ChevronUp,
  Sparkles,
  BarChart3,
  RefreshCw
} from 'lucide-react';

// Types
interface Recording {
  recordingId: string;
  timestamp: string;
  caller: string;
  callee: string;
  caller_name: string | null;
  callee_name: string | null;
  duration: number;
  audio_url: string | null;
  transcript_text: string | null;
  summary_text: string | null;
  processing_status: string;
  detected_language: string | null;
  sentiment: {
    score: number;
    label: string;
  } | null;
  key_topics: string[] | null;
  action_items: string[] | null;
  quality_score: number;
  source: string;
}

interface RecordingsStats {
  total_recordings: number;
  by_status: Record<string, number>;
  with_transcripts: number;
  with_summaries: number;
  average_quality_score: number;
  total_storage_mb: number;
}

export function RecordingsManager() {
  // Use relative URLs for production, or localhost for dev
  const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : '';

  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [stats, setStats] = useState<RecordingsStats | null>(null);
  const [selectedRecording, setSelectedRecording] = useState<Recording | null>(null);
  const [loading, setLoading] = useState(false);
  const [fetchingNew, setFetchingNew] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const [autoTranscribing, setAutoTranscribing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showFilters, setShowFilters] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);

  useEffect(() => {
    loadRecordings();
    loadStats();
  }, []);

  useEffect(() => {
    if (statusFilter !== 'all') {
      loadRecordings();
    }
  }, [statusFilter]);

  // Auto-transcribe when selecting a recording without transcript
  useEffect(() => {
    if (selectedRecording &&
        !selectedRecording.transcript_text &&
        selectedRecording.audio_url &&
        !autoTranscribing) {
      // Automatically start transcription
      autoTranscribeRecording(selectedRecording.recordingId);
    }
  }, [selectedRecording]);

  const loadRecordings = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (statusFilter !== 'all') {
        params.append('status', statusFilter);
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/recordings/?${params.toString()}`);
      const data = await response.json();

      // Handle both array and paginated response
      if (Array.isArray(data)) {
        setRecordings(data);
      } else if (data.items && Array.isArray(data.items)) {
        setRecordings(data.items);
      } else {
        setRecordings([]);
      }
    } catch (error) {
      console.error('Failed to load recordings:', error);
      setRecordings([]);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/recordings/stats/summary`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const fetchNewRecordings = async () => {
    setFetchingNew(true);
    setShowAIModal(true);
    try {
      await fetch(`${API_BASE_URL}/api/v1/recordings/fetch?hours=24`, {
        method: 'POST'
      });

      // Wait a bit for visual effect
      await new Promise(resolve => setTimeout(resolve, 2000));

      await loadRecordings();
      await loadStats();
    } catch (error) {
      console.error('Failed to fetch new recordings:', error);
    } finally {
      setFetchingNew(false);
      setShowAIModal(false);
    }
  };

  const transcribeRecording = async (recordingId: string) => {
    setTranscribing(true);
    setShowAIModal(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/recordings/${recordingId}/transcribe`,
        { method: 'POST' }
      );
      const data = await response.json();

      if (data.success) {
        await loadRecordings();
        if (selectedRecording?.recordingId === recordingId) {
          const updated = recordings.find(r => r.recordingId === recordingId);
          if (updated) setSelectedRecording(updated);
        }
      }
    } catch (error) {
      console.error('Failed to transcribe recording:', error);
    } finally {
      setTranscribing(false);
      setShowAIModal(false);
    }
  };

  const autoTranscribeRecording = async (recordingId: string) => {
    setAutoTranscribing(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/recordings/${recordingId}/transcribe`,
        { method: 'POST' }
      );
      const data = await response.json();

      if (data.success) {
        // Reload recordings to get updated data
        await loadRecordings();

        // Update the selected recording with new transcript
        if (selectedRecording?.recordingId === recordingId) {
          const updated = recordings.find(r => r.recordingId === recordingId);
          if (updated) {
            setSelectedRecording(updated);
          }
        }
      }
    } catch (error) {
      console.error('Failed to auto-transcribe recording:', error);
    } finally {
      setAutoTranscribing(false);
    }
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.3) return 'text-green-500';
    if (score < -0.3) return 'text-red-500';
    return 'text-yellow-500';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'partial': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-gray-100 text-gray-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  const filteredRecordings = (recordings || []).filter(recording => {
    if (!recording) return false;

    const matchesSearch = searchQuery === '' ||
      recording.caller?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      recording.callee?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      recording.transcript_text?.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesSearch;
  });

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* AI Loading Modal */}
      <AILoadingModal
        isOpen={showAIModal}
        message={fetchingNew ? "Obteniendo nuevas grabaciones de Webex..." : "Transcribiendo audio con Whisper AI..."}
      />

      {/* Header with Stats */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-3">
            <div className="p-3 bg-gradient-to-br from-[#E30519] to-red-600 rounded-xl shadow-lg">
              <FileAudio className="w-8 h-8 text-white" />
            </div>
            Grabaciones de Llamadas
          </h1>
          <p className="text-gray-600 mt-2">
            Gestiona y analiza tus grabaciones de Webex Calling con transcripción impulsada por IA
          </p>
        </div>
        <Button
          onClick={fetchNewRecordings}
          disabled={fetchingNew}
          className="bg-gradient-to-r from-[#E30519] to-red-600 hover:from-red-600 hover:to-[#E30519] text-white shadow-lg"
        >
          {fetchingNew ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Obteniendo...
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4 mr-2" />
              Obtener Nuevas Grabaciones
            </>
          )}
        </Button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="border-2 border-gray-100 hover:border-[#E30519] transition-all hover:shadow-lg">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total de Grabaciones</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total_recordings}</p>
                </div>
                <div className="p-3 bg-blue-100 rounded-lg">
                  <BarChart3 className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-gray-100 hover:border-[#E30519] transition-all hover:shadow-lg">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Con Transcripción</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.with_transcripts}</p>
                </div>
                <div className="p-3 bg-green-100 rounded-lg">
                  <MessageSquare className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-gray-100 hover:border-[#E30519] transition-all hover:shadow-lg">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Puntuación de Calidad</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">
                    {(stats.average_quality_score * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="p-3 bg-purple-100 rounded-lg">
                  <Sparkles className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-gray-100 hover:border-[#E30519] transition-all hover:shadow-lg">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Almacenamiento Usado</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">
                    {stats.total_storage_mb.toFixed(1)} MB
                  </p>
                </div>
                <div className="p-3 bg-orange-100 rounded-lg">
                  <Download className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                type="text"
                placeholder="Buscar por llamante, destinatario o contenido de transcripción..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 border-2 focus:border-[#E30519]"
              />
            </div>
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border-2 border-gray-200 rounded-md focus:border-[#E30519] focus:outline-none"
              >
                <option value="all">Todos los Estados</option>
                <option value="completed">Completado</option>
                <option value="partial">Parcial</option>
                <option value="pending">Pendiente</option>
                <option value="failed">Fallido</option>
              </select>
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className="border-2"
              >
                <Filter className="w-4 h-4 mr-2" />
                Filtros
                {showFilters ? <ChevronUp className="w-4 h-4 ml-2" /> : <ChevronDown className="w-4 h-4 ml-2" />}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recordings List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* List of recordings */}
        <div className="space-y-4">
          {loading ? (
            <Card>
              <CardContent className="py-12">
                <div className="flex items-center justify-center">
                  <Loader2 className="w-8 h-8 animate-spin text-[#E30519]" />
                </div>
              </CardContent>
            </Card>
          ) : filteredRecordings.length === 0 ? (
            <Card>
              <CardContent className="py-12">
                <div className="text-center text-gray-500">
                  <FileAudio className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>No se encontraron grabaciones</p>
                  <Button
                    onClick={fetchNewRecordings}
                    className="mt-4 bg-[#E30519] hover:bg-red-600"
                  >
                    Obtener Nuevas Grabaciones
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            filteredRecordings.map((recording) => (
              <AIBorder key={recording.recordingId}>
                <Card
                  className={`cursor-pointer transition-all hover:shadow-xl ${
                    selectedRecording?.recordingId === recording.recordingId
                      ? 'ring-2 ring-[#E30519] shadow-lg'
                      : ''
                  }`}
                  onClick={() => setSelectedRecording(recording)}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg flex items-center gap-2">
                          <Mic className="w-5 h-5 text-[#E30519]" />
                          {recording.caller || 'Llamante Desconocido'}
                        </CardTitle>
                        <CardDescription className="mt-1">
                          Llamó a: {recording.callee || 'Desconocido'}
                        </CardDescription>
                      </div>
                      <span className={`px-3 py-1 text-xs font-semibold rounded-full ${getStatusColor(recording.processing_status)}`}>
                        {recording.processing_status}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="flex items-center gap-2 text-gray-600">
                        <Clock className="w-4 h-4" />
                        <span>{new Date(recording.timestamp).toLocaleString()}</span>
                      </div>
                      <div className="flex items-center gap-2 text-gray-600">
                        <TrendingUp className="w-4 h-4" />
                        <span>{recording.duration}s</span>
                      </div>
                    </div>

                    {recording.sentiment && (
                      <div className="mt-3 flex items-center gap-2">
                        <span className="text-sm text-gray-600">Sentimiento:</span>
                        <span className={`text-sm font-semibold ${getSentimentColor(recording.sentiment.score)}`}>
                          {recording.sentiment.label} ({(recording.sentiment.score * 100).toFixed(0)}%)
                        </span>
                      </div>
                    )}

                    {recording.transcript_text && (
                      <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                        <p className="text-sm text-gray-700 line-clamp-2">
                          {recording.transcript_text}
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </AIBorder>
            ))
          )}
        </div>

        {/* Selected Recording Detail */}
        <div className="lg:sticky lg:top-6 h-fit">
          {selectedRecording ? (
            <AIBorder>
              <Card className="shadow-2xl">
                <CardHeader className="bg-gradient-to-r from-[#E30519] to-red-600 text-white">
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="w-6 h-6" />
                    Detalles de la Grabación
                  </CardTitle>
                  <CardDescription className="text-white/90">
                    {selectedRecording.recordingId}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6 pt-6">
                  {/* Audio Player */}
                  {selectedRecording.audio_url && (
                    <div>
                      <AudioPlayer
                        audioUrl={selectedRecording.audio_url}
                        title={`Grabación de Llamada: ${selectedRecording.caller} → ${selectedRecording.callee}`}
                      />
                    </div>
                  )}

                  {/* Transcript */}
                  {selectedRecording.transcript_text ? (
                    <div>
                      <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                        <MessageSquare className="w-5 h-5 text-[#E30519]" />
                        Transcripción
                      </h3>
                      <div className="p-4 bg-gray-50 rounded-lg max-h-64 overflow-y-auto">
                        <p className="text-sm text-gray-700 whitespace-pre-wrap">
                          {selectedRecording.transcript_text}
                        </p>
                      </div>
                      <div className="mt-2 text-xs text-gray-500">
                        Fuente: {selectedRecording.source} | Idioma: {selectedRecording.detected_language || 'N/A'}
                      </div>
                    </div>
                  ) : autoTranscribing ? (
                    <div className="p-8 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg text-center border-2 border-dashed border-blue-200">
                      <div className="relative">
                        <Brain className="w-16 h-16 mx-auto mb-4 text-[#E30519] animate-pulse" />
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-20 h-20 border-4 border-[#E30519] border-t-transparent rounded-full animate-spin"></div>
                        </div>
                      </div>
                      <h4 className="text-lg font-semibold text-gray-800 mb-2 mt-4">
                        Analizando audio con Whisper AI...
                      </h4>
                      <p className="text-sm text-gray-600 mb-3">
                        Nuestro modelo de IA está procesando la grabación y generando la transcripción
                      </p>
                      <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                        <div className="w-2 h-2 bg-[#E30519] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-[#E30519] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-[#E30519] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-6 bg-gray-50 rounded-lg text-center">
                      <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                      <p className="text-gray-600 mb-4">No hay transcripción disponible</p>
                      {selectedRecording.audio_url && (
                        <Button
                          onClick={() => transcribeRecording(selectedRecording.recordingId)}
                          disabled={transcribing}
                          className="bg-gradient-to-r from-[#E30519] to-red-600 text-white"
                        >
                          {transcribing ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Transcribiendo...
                            </>
                          ) : (
                            <>
                              <Brain className="w-4 h-4 mr-2" />
                              Transcribir con Whisper AI
                            </>
                          )}
                        </Button>
                      )}
                    </div>
                  )}

                  {/* Summary */}
                  {selectedRecording.summary_text && (
                    <div>
                      <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                        <Brain className="w-5 h-5 text-[#E30519]" />
                        Resumen con IA
                      </h3>
                      <div className="p-4 bg-blue-50 rounded-lg">
                        <p className="text-sm text-gray-700">
                          {selectedRecording.summary_text}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Key Topics */}
                  {selectedRecording.key_topics && selectedRecording.key_topics.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-lg mb-3">Temas Clave</h3>
                      <div className="flex flex-wrap gap-2">
                        {selectedRecording.key_topics.map((topic, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Action Items */}
                  {selectedRecording.action_items && selectedRecording.action_items.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                        Acciones a Seguir
                      </h3>
                      <ul className="space-y-2">
                        {selectedRecording.action_items.map((item, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <div className="mt-1 w-2 h-2 rounded-full bg-green-500 flex-shrink-0"></div>
                            <span className="text-sm text-gray-700">{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            </AIBorder>
          ) : (
            <Card className="shadow-lg">
              <CardContent className="py-24">
                <div className="text-center text-gray-400">
                  <FileAudio className="w-20 h-20 mx-auto mb-4 opacity-30" />
                  <p className="text-lg">Selecciona una grabación para ver detalles</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
