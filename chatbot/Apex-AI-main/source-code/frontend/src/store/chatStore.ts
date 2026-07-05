import { create } from 'zustand'
import { APP_CONFIG } from '../config'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  agentRole?: string
  analysisType?: string
  confidence?: 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW' | 'VERY_LOW' | 'UNKNOWN'
}

interface ChatState {
  responseMode: string
  messages: Message[]
  isTyping: boolean
  addMessage: (msg: Message) => void
  setTyping: (typing: boolean) => void
  setResponseMode: (mode: string) => void
}

export const useChatStore = create<ChatState>()((set) => ({
  responseMode: 'MODE_BUSINESS',
  messages: [
    {
      id: '1',
      role: 'assistant',
      content: `Hello! I am ${APP_CONFIG.CHATBOT_NAME}. How can I assist you with your analytics today?`,
      agentRole: 'DescriptiveAnalyticsAgent',
      confidence: 'VERY_HIGH'
    }
  ],
  isTyping: false,
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  setTyping: (typing) => set({ isTyping: typing }),
  setResponseMode: (mode) => set({ responseMode: mode })
}))
