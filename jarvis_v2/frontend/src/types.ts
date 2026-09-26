export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  streaming?: boolean;
  metadata?: {
    tools_used?: string[];
    execution_time?: number;
    validation_score?: number;
  };
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: Date;
  updated_at: Date;
  message_count: number;
}

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  preferences: {
    theme: 'dark' | 'light';
    language: string;
    voice_enabled: boolean;
  };
  created_at: Date;
}

export interface ToolExecution {
  tool_id: string;
  parameters: Record<string, any>;
  success: boolean;
  execution_time: number;
  error?: string;
}
