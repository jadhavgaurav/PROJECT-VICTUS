import { create } from 'zustand';
import type { AgentPhase, ChatMessage, ToolCall } from '../types';

interface AgentStore {
  phase: AgentPhase;
  phaseMessage: string;
  messages: ChatMessage[];
  toolCalls: ToolCall[];
  streamingContent: string;
  
  setPhase: (phase: AgentPhase, message?: string) => void;
  setMessages: (messages: ChatMessage[]) => void;
  addMessage: (message: ChatMessage) => void;
  updateStreamingContent: (delta: string) => void;
  commitStreamingContent: () => void;
  
  addToolCall: (toolCall: ToolCall) => void;
  updateToolCall: (id: string, update: Partial<ToolCall>) => void;
  clearToolCalls: () => void;
  
  reset: () => void;
}

export const useAgentStore = create<AgentStore>((set) => ({
  phase: 'idle',
  phaseMessage: '',
  messages: [],
  toolCalls: [],
  streamingContent: '',
  
  setPhase: (phase, message = '') => set({ phase, phaseMessage: message }),
  
  setMessages: (messages) => set({ messages }),

  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  
  updateStreamingContent: (delta) => set((state) => ({ 
    streamingContent: state.streamingContent + delta 
  })),
  
  commitStreamingContent: () => set((state) => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'assistant',
      content: state.streamingContent,
      timestamp: Date.now(),
    };
    return {
      messages: [...state.messages, newMessage],
      streamingContent: '',
    };
  }),
  
  addToolCall: (toolCall) => set((state) => ({
    toolCalls: [...state.toolCalls, toolCall]
  })),
  
  updateToolCall: (id, update) => set((state) => ({
    toolCalls: state.toolCalls.map(tc => 
      tc.id === id ? { ...tc, ...update } : tc
    )
  })),
  
  clearToolCalls: () => set({ toolCalls: [] }),

  reset: () => set({
    phase: 'idle',
    phaseMessage: '',
    messages: [],
    toolCalls: [],
    streamingContent: ''
  })
}));
