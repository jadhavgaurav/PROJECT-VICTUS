export type AgentPhase = 
  | 'idle'
  | 'connecting'
  | 'thinking'
  | 'retrieving'
  | 'using_tools'
  | 'synthesizing'
  | 'done'
  | 'error';

export interface ToolCall {
  id: string;
  name: string;
  input: any;
  status: 'running' | 'completed' | 'failed' | 'requires_action';
  result?: string;
  startTime: number;
  endTime?: number;
  duration?: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface AgentState {
  phase: AgentPhase;
  phaseMessage: string;
  messages: ChatMessage[];
  toolCalls: ToolCall[];
  activeToolId: string | null;
  streamingContent: string;
}
