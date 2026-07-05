import { create } from 'zustand';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  agentRole?: string;
  analysisType?: string;
  confidence?: string;
}

interface ChatState {
  responseMode: string;
  messages: Message[];
  conversationId: string | null;
  isTyping: boolean;
  addMessage: (msg: Message) => void;
  setTyping: (typing: boolean) => void;
  setResponseMode: (mode: string) => void;
  setConversationId: (id: string | null) => void;
  resetChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  responseMode: 'MODE_BUSINESS',
  messages: [
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I am your AI Analytics Assistant. How can I assist you with your ingested data and insights today?',
      agentRole: 'DescriptiveAnalyticsAgent',
      confidence: 'VERY_HIGH',
    },
  ],
  conversationId: null,
  isTyping: false,
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  setTyping: (typing) => set({ isTyping: typing }),
  setResponseMode: (mode) => set({ responseMode: mode }),
  setConversationId: (id) => set({ conversationId: id }),
  resetChat: () => set({
    conversationId: null,
    messages: [
      {
        id: '1',
        role: 'assistant',
        content: 'Hello! I am your AI Analytics Assistant. How can I assist you with your ingested data and insights today?',
        agentRole: 'DescriptiveAnalyticsAgent',
        confidence: 'VERY_HIGH',
      },
    ],
  }),
}));
