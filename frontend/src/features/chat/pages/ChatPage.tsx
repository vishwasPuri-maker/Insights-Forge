import React, { useState, useRef, useEffect } from 'react';
import { OSLayout } from '@/components/layout/OSLayout';
import { OSSection } from '@/components/layout/OSSection';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useChatStore } from '@/store/chatStore';
import { apiClient } from '@/services/apiClient';
import { Send, Bot, Sparkles, User, AlertCircle } from 'lucide-react';
import type { Message } from '@/store/chatStore';

export const ChatPage: React.FC = () => {
  const [input, setInput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const {
    messages,
    isTyping,
    responseMode,
    conversationId,
    addMessage,
    setTyping,
    setResponseMode,
    setConversationId,
    resetChat,
  } = useChatStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userText = input;
    setInput('');
    setError(null);

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: userText,
    };
    addMessage(userMsg);
    setTyping(true);

    try {
      const response = await apiClient.post('/chat/completions', {
        query: userText,
        conversation_id: conversationId || undefined,
        response_mode: responseMode,
        stream: false,
      });

      const data = response.data;
      if (data.status === 'success' || data.message) {
        if (data.conversation_id) {
          setConversationId(data.conversation_id);
        }

        const assistantMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message,
          agentRole: data.agent,
          analysisType: data.analysis_type,
          confidence: data.confidence,
        };
        addMessage(assistantMsg);
      } else {
        throw new Error(data.error_details || 'Failed to generate response');
      }
    } catch (err: any) {
      console.error('Chat completions error:', err);
      setError(err?.message || 'The AI assistant service encountered an error. Please try again.');
    } finally {
      setTyping(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  return (
    <OSLayout title="AI Assistant Command Center" description="Data-grounded chat powered by Gemini LLM">
      <OSSection title="AI Chat Terminal" description="Query your ingested tenant datasets securely with tenant isolation and prompt injection safety.">
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 items-start">
          {/* Main Chat Interface */}
          <div className="xl:col-span-3 flex flex-col h-[650px] border border-border/50 bg-card rounded-xl overflow-hidden shadow-2xl">
            {/* Header controls */}
            <div className="bg-muted/40 border-b border-border/40 p-4 flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
              <div className="flex items-center gap-3">
                <Sparkles className="h-5 w-5 text-brand-primary animate-pulse" />
                <span className="font-semibold text-foreground text-body">Gemini Agent Intelligence</span>
                <select
                  value={responseMode}
                  onChange={(e) => setResponseMode(e.target.value)}
                  className="text-xs font-normal border border-border/60 rounded px-2 py-1 bg-card text-foreground focus:outline-none focus:ring-1 focus:ring-brand-primary"
                >
                  <option value="MODE_BUSINESS">Business Mode</option>
                  <option value="MODE_EXECUTIVE">Executive Mode</option>
                  <option value="MODE_TECHNICAL">Technical Mode</option>
                  <option value="MODE_CONCISE">Concise Mode</option>
                  <option value="MODE_ANALYST">Analyst Mode</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-normal text-brand-success bg-brand-success/10 border border-brand-success/20 px-2 py-0.5 rounded-full">
                  Real-time Grounding Active
                </span>
                <Button variant="outline" size="sm" onClick={resetChat} className="text-xs h-7 py-1 px-3">
                  Clear Chat
                </Button>
              </div>
            </div>

            {/* Message Pane */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {messages.map((m) => (
                <div key={m.id} className={`flex gap-4 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {m.role === 'assistant' && (
                    <div className="w-9 h-9 rounded-full bg-brand-primary/10 border border-brand-primary/20 flex items-center justify-center text-brand-primary shrink-0">
                      <Bot size={20} />
                    </div>
                  )}

                  <div className={`flex flex-col gap-1.5 max-w-[85%] ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
                    <div className={`rounded-xl p-4 text-sm leading-relaxed shadow-sm ${
                      m.role === 'user'
                        ? 'bg-brand-primary text-white rounded-tr-none'
                        : 'bg-muted/50 text-foreground border border-border/40 rounded-tl-none'
                    }`}>
                      <p className="whitespace-pre-line">{m.content}</p>

                      {m.agentRole && (
                        <div className="mt-3 pt-2.5 border-t border-border/30 flex gap-2 flex-wrap items-center">
                          <span className="text-xs text-muted-foreground bg-card/60 border border-border/40 px-2 py-0.5 rounded font-mono">
                            {m.agentRole}
                          </span>
                          {m.analysisType && (
                            <span className="text-xs text-brand-primary bg-brand-primary/10 border border-brand-primary/20 px-2 py-0.5 rounded font-mono">
                              {m.analysisType}
                            </span>
                          )}
                          <span className={`text-xs px-2 py-0.5 rounded font-mono ${
                            m.confidence === 'VERY_HIGH' || m.confidence === 'HIGH'
                              ? 'text-brand-success bg-brand-success/10 border border-brand-success/20'
                              : m.confidence === 'MEDIUM'
                              ? 'text-brand-warning bg-brand-warning/10 border border-brand-warning/20'
                              : 'text-brand-error bg-brand-error/10 border border-brand-error/20'
                          }`}>
                            {m.confidence} Confidence
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {m.role === 'user' && (
                    <div className="w-9 h-9 rounded-full bg-brand-primary/10 border border-brand-primary/20 flex items-center justify-center text-brand-primary shrink-0">
                      <User size={18} />
                    </div>
                  )}
                </div>
              ))}

              {isTyping && (
                <div className="flex gap-4 items-center text-muted-foreground">
                  <div className="w-9 h-9 rounded-full bg-brand-primary/10 border border-brand-primary/20 flex items-center justify-center text-brand-primary shrink-0 animate-spin">
                    <Bot size={20} />
                  </div>
                  <span className="text-sm italic">AI Assistant is analyzing dataset context...</span>
                </div>
              )}

              {error && (
                <div className="flex gap-3 bg-brand-error/10 border border-brand-error/20 text-brand-error p-4 rounded-lg items-start text-sm">
                  <AlertCircle size={20} className="shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold">Inference Error:</span> {error}
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Form */}
            <div className="p-4 border-t border-border/50 bg-muted/20 flex gap-3">
              <input
                type="text"
                disabled={isTyping}
                className="flex-1 border border-border bg-card text-foreground rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/50 disabled:opacity-50"
                placeholder="Ask a question about your ingested data (e.g. 'What is the average revenue?')"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              />
              <Button onClick={handleSend} disabled={isTyping} className="shrink-0">
                <Send size={18} />
              </Button>
            </div>
          </div>

          {/* Quick Prompts Panel */}
          <div className="space-y-6">
            <Card>
              <CardContent className="pt-6">
                <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-wider mb-3">Suggested Queries</h3>
                <div className="space-y-2.5">
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left text-xs whitespace-normal h-auto py-2.5"
                    onClick={() => handleSuggestionClick('How many records are in this dataset?')}
                  >
                    How many records are in this dataset?
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left text-xs whitespace-normal h-auto py-2.5"
                    onClick={() => handleSuggestionClick('What is the total revenue in this dataset?')}
                  >
                    What is the total revenue in this dataset?
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left text-xs whitespace-normal h-auto py-2.5"
                    onClick={() => handleSuggestionClick('What is the average revenue in this dataset?')}
                  >
                    What is the average revenue in this dataset?
                  </Button>
                  <Button
                    variant="outline"
                    className="w-full justify-start text-left text-xs whitespace-normal h-auto py-2.5"
                    onClick={() => handleSuggestionClick('Summarize the most important insights.')}
                  >
                    Summarize the most important insights.
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6 text-xs text-muted-foreground space-y-2">
                <h3 className="font-bold text-foreground mb-1 uppercase tracking-wider">AI Guardrails</h3>
                <p>✓ Tenant isolation is enforced dynamically based on your authenticated JWT.</p>
                <p>✓ The model operates in strict read-only mode and cannot perform modifications.</p>
                <p>✓ Real-time grounding uses your primary workspace vector embeddings.</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </OSSection>
    </OSLayout>
  );
};
