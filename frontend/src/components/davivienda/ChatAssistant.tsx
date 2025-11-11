import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Loader2, Send, Sparkles, Download, Info, Brain } from 'lucide-react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  details?: any;
  timestamp?: string;
  isTyping?: boolean;
}

interface ExampleCategory {
  category: string;
  questions: string[];
}

// Thinking animation component
const ThinkingAnimation = () => {
  return (
    <div className="flex items-center gap-3 text-gray-500 bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-lg mr-12 border border-gray-200">
      <div className="relative">
        <Brain className="h-5 w-5 text-davivienda-red animate-pulse" />
        <div className="absolute inset-0 bg-davivienda-red/20 rounded-full animate-ping" />
      </div>
      <div className="flex flex-col">
        <span className="text-sm font-medium text-gray-700">Analizando tus datos</span>
        <div className="flex gap-1 mt-1">
          <span className="w-1.5 h-1.5 bg-davivienda-red rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="w-1.5 h-1.5 bg-davivienda-red rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="w-1.5 h-1.5 bg-davivienda-red rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
};

// Typewriter component
const TypewriterText = ({ text, onComplete }: { text: string; onComplete?: () => void }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, 20); // 20ms per character for smooth typing

      return () => clearTimeout(timeout);
    } else if (onComplete && currentIndex === text.length && displayedText.length > 0) {
      onComplete();
    }
  }, [currentIndex, text, onComplete, displayedText.length]);

  return <span>{displayedText}</span>;
};

export function ChatAssistant() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [examples, setExamples] = useState<ExampleCategory[]>([]);
  const [showExamples, setShowExamples] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load examples
  const loadExamples = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/chat/examples');
      const data = await response.json();

      const examplesList: ExampleCategory[] = Object.entries(data.categories).map(
        ([category, questions]) => ({
          category,
          questions: questions as string[]
        })
      );

      setExamples(examplesList);
      setShowExamples(true);
    } catch (error) {
      console.error('Error loading examples:', error);
    }
  };

  const sendMessage = async (questionText?: string) => {
    const question = questionText || message;
    if (!question.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: question }]);
    setMessage('');
    setLoading(true);
    setIsThinking(true);

    try {
      // Show thinking animation for 2 seconds minimum
      const startTime = Date.now();

      const response = await fetch('http://localhost:8000/api/v1/chat/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          hours: 24,
          limit: 200
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Ensure thinking animation shows for at least 2 seconds
      const elapsedTime = Date.now() - startTime;
      const remainingTime = Math.max(0, 2000 - elapsedTime);

      await new Promise(resolve => setTimeout(resolve, remainingTime));

      setIsThinking(false);

      // Add assistant response with typing effect
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        details: data.details,
        timestamp: data.timestamp,
        isTyping: true
      }]);
    } catch (error) {
      console.error('Error:', error);
      setIsThinking(false);

      let errorMessage = 'No se pudo procesar la pregunta. Por favor intenta de nuevo.';

      if (error instanceof Error) {
        if (error.message.includes('500')) {
          errorMessage = '⚠️ El servidor está procesando demasiadas peticiones. Por favor espera unos segundos e intenta de nuevo.\n\nEsto puede ocurrir cuando el API de Webex ha alcanzado su límite de peticiones.';
        } else {
          errorMessage = error.message;
        }
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: errorMessage,
        isTyping: false
      }]);
    } finally {
      setLoading(false);
    }
  };

  const downloadChatReport = async (questionText: string, answerData: any) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/reports/chat/pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: questionText,
          hours: 24,
          limit: 200
        })
      });

      if (!response.ok) throw new Error('Failed to generate report');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `chat_report_${new Date().getTime()}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading report:', error);
    }
  };

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isThinking]);

  return (
    <div className="space-y-4">
      <Card className="border-l-4 border-l-davivienda-red">
        <CardHeader className="bg-gradient-to-r from-gray-50 to-white">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <CardTitle className="flex items-center gap-2 text-2xl">
                <div className="relative">
                  <Sparkles className="h-6 w-6 text-davivienda-red animate-pulse" />
                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-davivienda-red rounded-full animate-ping" />
                </div>
                <span className="bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  Asistente de Consultas IA
                </span>
              </CardTitle>
              <CardDescription className="mt-2 text-base">
                Haz preguntas sobre tus datos de llamadas en <span className="font-semibold text-davivienda-red">lenguaje natural</span>
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadExamples}
              className="hover:bg-davivienda-red hover:text-white transition-colors"
            >
              <Info className="h-4 w-4 mr-2" />
              Ver ejemplos
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Examples Modal */}
          {showExamples && (
            <div className="mb-4 p-4 bg-gray-50 rounded-lg border">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-sm">Preguntas de Ejemplo</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowExamples(false)}
                >
                  Cerrar
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {examples.map((category) => (
                  <div key={category.category}>
                    <h4 className="font-medium text-xs text-gray-600 mb-2">
                      {category.category}
                    </h4>
                    <div className="space-y-1">
                      {category.questions.slice(0, 3).map((q, idx) => (
                        <button
                          key={idx}
                          onClick={() => {
                            setShowExamples(false);
                            sendMessage(q);
                          }}
                          className="text-xs text-left w-full p-2 hover:bg-white rounded border border-transparent hover:border-davivienda-red/20 transition-colors"
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Chat Messages */}
          <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
            {messages.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Sparkles className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p className="text-sm">Haz tu primera pregunta para empezar</p>
                <p className="text-xs mt-1">Ejemplo: "¿Cuál es la cola que más llamadas tiene?"</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-davivienda-red text-white ml-12'
                      : 'bg-gray-100 mr-12'
                  }`}
                >
                  <div className="text-sm font-medium mb-1">
                    {msg.role === 'user' ? 'Tú' : 'Asistente IA'}
                  </div>
                  <div className="text-sm whitespace-pre-wrap">
                    {msg.isTyping ? (
                      <TypewriterText
                        text={msg.content}
                        onComplete={() => {
                          // Mark typing as complete
                          setMessages(prev => prev.map((m, i) =>
                            i === idx ? { ...m, isTyping: false } : m
                          ));
                        }}
                      />
                    ) : (
                      msg.content
                    )}
                  </div>

                  {msg.details && (
                    <div className="mt-3 space-y-2">
                      {/* Key Metrics */}
                      {msg.details.key_metrics && (
                        <div className="bg-white/50 p-3 rounded text-xs">
                          <div className="font-semibold mb-2 text-davivienda-red">📊 Métricas Clave</div>
                          <div className="space-y-2">
                            {Object.entries(msg.details.key_metrics).map(([key, value]) => {
                              // Check if value is an array of objects (like top_agents)
                              if (Array.isArray(value) && value.length > 0 && typeof value[0] === 'object') {
                                return (
                                  <div key={key} className="mt-2">
                                    <div className="font-medium text-gray-700 mb-1 capitalize">
                                      {key.replace(/_/g, ' ')}:
                                    </div>
                                    <div className="overflow-x-auto">
                                      <table className="min-w-full text-xs border border-gray-200">
                                        <thead className="bg-gray-100">
                                          <tr>
                                            {Object.keys(value[0]).map((col) => (
                                              <th key={col} className="px-2 py-1 border-b text-left font-semibold capitalize">
                                                {col.replace(/_/g, ' ')}
                                              </th>
                                            ))}
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {value.map((row: any, idx: number) => (
                                            <tr key={idx} className="border-b hover:bg-gray-50">
                                              {Object.values(row).map((cell: any, cellIdx: number) => (
                                                <td key={cellIdx} className="px-2 py-1">
                                                  {typeof cell === 'number' && cell % 1 !== 0
                                                    ? cell.toFixed(2)
                                                    : String(cell)}
                                                </td>
                                              ))}
                                            </tr>
                                          ))}
                                        </tbody>
                                      </table>
                                    </div>
                                  </div>
                                );
                              }
                              // Regular key-value pairs
                              return (
                                <div key={key} className="flex justify-between items-center py-1 border-b border-gray-200 last:border-0">
                                  <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}:</span>
                                  <span className="font-semibold text-gray-900">
                                    {typeof value === 'number' && value % 1 !== 0
                                      ? value.toFixed(2)
                                      : String(value)}
                                  </span>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      )}

                      {/* Insights */}
                      {msg.details.insights && msg.details.insights.length > 0 && (
                        <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded text-xs">
                          <div className="font-semibold mb-2 text-blue-800 flex items-center gap-1">
                            💡 Observaciones
                          </div>
                          <ul className="space-y-1.5">
                            {msg.details.insights.map((insight: string, i: number) => (
                              <li key={i} className="flex items-start gap-2">
                                <span className="text-blue-600 mt-0.5">•</span>
                                <span className="text-gray-700">{insight}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Recommendations */}
                      {msg.details.recommendations && msg.details.recommendations.length > 0 && (
                        <div className="bg-green-50 border-l-4 border-green-400 p-3 rounded text-xs">
                          <div className="font-semibold mb-2 text-green-800 flex items-center gap-1">
                            ✅ Recomendaciones
                          </div>
                          <ul className="space-y-1.5">
                            {msg.details.recommendations.map((rec: string, i: number) => (
                              <li key={i} className="flex items-start gap-2">
                                <span className="text-green-600 mt-0.5">→</span>
                                <span className="text-gray-700">{rec}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Download button for assistant messages */}
                      {msg.role === 'assistant' && idx > 0 && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="mt-2 text-xs"
                          onClick={() => downloadChatReport(messages[idx - 1].content, msg)}
                        >
                          <Download className="h-3 w-3 mr-1" />
                          Descargar PDF
                        </Button>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}

            {isThinking && <ThinkingAnimation />}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="flex gap-2">
            <Input
              placeholder="Escribe tu pregunta aquí..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !loading) {
                  sendMessage();
                }
              }}
              disabled={loading}
            />
            <Button
              onClick={() => sendMessage()}
              disabled={loading || !message.trim()}
              className="bg-davivienda-red hover:bg-davivienda-red/90"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
