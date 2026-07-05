import { useState } from 'react'
import { Send, Bot } from 'lucide-react'
import { useChatStore } from '../store/chatStore'
import { APP_CONFIG } from '../config'

export const ChatInterface = () => {
  const [input, setInput] = useState('')
  const { messages, isTyping, responseMode, addMessage, setTyping, setResponseMode } = useChatStore()

  const handleSend = async () => {
    if (!input.trim()) return
    
    const userMsg = { id: Date.now().toString(), role: 'user' as const, content: input }
    addMessage(userMsg)
    setInput('')
    setTyping(true)

    // Simulate API call to FastAPI backend
    setTimeout(() => {
      const isViolation = input.toLowerCase().includes('delete') || input.toLowerCase().includes('drop')
      const q = input.toLowerCase()
      
      // Feature 7: Simulate backend intent classification
      let analysisType = 'kpi_analysis'
      let agent = 'KPIAnalysisAgent'
      let confidence: 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW' | 'VERY_LOW' | 'UNKNOWN' = 'VERY_HIGH'
      
      if (q.includes('forecast') || q.includes('predict')) { analysisType = 'forecasting'; agent = 'PredictiveAnalyticsAgent'; confidence = 'LOW' }
      else if (q.includes('anomaly') || q.includes('spike') || q.includes('unexpected')) { analysisType = 'anomaly_detection'; agent = 'AnomalyDetectionAgent'; confidence = 'MEDIUM' }
      else if (q.includes('recommend') || q.includes('improve')) { analysisType = 'recommendation'; agent = 'RecommendationAgent'; confidence = 'MEDIUM' }
      else if (q.includes('compare') || q.includes('vs')) { analysisType = 'comparative_analysis'; agent = 'ComparativeAnalysisAgent'; confidence = 'HIGH' }
      else if (q.includes('trend') || q.includes('growth')) { analysisType = 'trend_analysis'; agent = 'TrendAnalysisAgent'; confidence = 'HIGH' }
      else if (q.includes('dashboard') || q.includes('chart')) { analysisType = 'dashboard_explanation'; agent = 'DashboardExplanationAgent'; confidence = 'HIGH' }
      else if (q.includes('summary') || q.includes('summarize')) { analysisType = 'executive_summary'; agent = 'ExecutiveSummaryAgent'; confidence = 'VERY_HIGH' }
      
      let mockContent = `Based on the analysis, I found the following: Searching vector space for: ${input}`;
      if (responseMode === 'MODE_EXECUTIVE') mockContent = `Executive Summary:\nSearching vector space for: ${input}\n\nBusiness Impact:\nPositive growth trajectory.\n\nConfidence: HIGH`;
      if (responseMode === 'MODE_TECHNICAL') mockContent = `Methodology:\nVector Similarity Search\n\nDataset:\nBusiness Telemetry DB\n\nAnalysis:\nSearching vector space for: ${input}\n\nLimitations:\nMock environment constraints applied.`;
      if (responseMode === 'MODE_CONCISE') mockContent = `Searching vector space for: ${input}`;

      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: isViolation ? 'Action forbidden: Read-only access enforced. I cannot modify database state.' : mockContent,
        agentRole: isViolation ? 'SecurityAgent' : agent,
        analysisType: isViolation ? undefined : analysisType,
        confidence: isViolation ? 'HIGH' : confidence
      })
      setTyping(false)
    }, 1500)
  }

  return (
    <div className="flex flex-col h-[600px] border border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm mt-6">
      <div className="bg-gray-50 border-b border-gray-200 p-4 font-semibold text-gray-700 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <span>{APP_CONFIG.CHATBOT_NAME} Assistant</span>
          <select 
            value={responseMode} 
            onChange={(e) => setResponseMode(e.target.value)}
            className="text-xs font-normal border border-gray-300 rounded px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="MODE_BUSINESS">Business Mode</option>
            <option value="MODE_EXECUTIVE">Executive Mode</option>
            <option value="MODE_TECHNICAL">Technical Mode</option>
            <option value="MODE_CONCISE">Concise Mode</option>
            <option value="MODE_ANALYST">Analyst Mode</option>
          </select>
        </div>
        <span className="text-xs font-normal text-green-600 bg-green-100 px-2 py-1 rounded-full">Secure Analytics Mode</span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m) => (
          <div key={m.id} className={`flex gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 shrink-0">
                <Bot size={18} />
              </div>
            )}
            <div className={`max-w-[80%] rounded-lg p-3 text-sm ${
              m.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-gray-100 text-gray-800 rounded-bl-none'
            }`}>
              <p>{m.content}</p>
              {m.agentRole && (
                <div className="mt-2 text-xs flex gap-2 flex-wrap">
                  <span className="text-gray-500 bg-gray-200 px-1 rounded">{m.agentRole}</span>
                  {m.analysisType && (
                    <span className="text-indigo-700 bg-indigo-100 px-1 rounded">{m.analysisType}</span>
                  )}
                  <span className={`px-1 rounded ${
                    m.confidence === 'VERY_HIGH' || m.confidence === 'HIGH' ? 'text-green-700 bg-green-200' : 
                    m.confidence === 'MEDIUM' ? 'text-yellow-700 bg-yellow-200' : 
                    m.confidence === 'LOW' || m.confidence === 'VERY_LOW' ? 'text-orange-700 bg-orange-200' :
                    'text-red-700 bg-red-200'
                  }`}>
                    {m.confidence} Confidence
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex gap-3 text-gray-400 items-center">
             <Bot size={18} />
             <span className="text-sm">{APP_CONFIG.CHATBOT_NAME} is analyzing...</span>
          </div>
        )}
      </div>

      <div className="p-3 border-t border-gray-200 bg-white flex gap-2">
        <input 
          type="text" 
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ask a question about your analytics (e.g. 'Why did revenue drop?')"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button 
          onClick={handleSend}
          className="bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 transition-colors"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  )
}
