import { create } from 'zustand';
import { Message, ChatSession, UserProfile } from './types';

interface AppState {
  messages: Message[];
  sessions: ChatSession[];
  currentSession: string | null;
  user: UserProfile | null;
  
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setCurrentSession: (sessionId: string) => void;
  createSession: (title: string) => void;
  setUser: (user: UserProfile) => void;
}

export const useStore = create<AppState>((set) => ({
  messages: [],
  sessions: [],
  currentSession: null,
  user: null,
  
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message]
    })),
  
  clearMessages: () => set({ messages: [] }),
  
  setCurrentSession: (sessionId) =>
    set({ currentSession: sessionId }),
  
  createSession: (title) =>
    set((state) => {
      const newSession: ChatSession = {
        id: Date.now().toString(),
        title,
        created_at: new Date(),
        updated_at: new Date(),
        message_count: 0
      };
      return {
        sessions: [...state.sessions, newSession],
        currentSession: newSession.id
      };
    }),
  
  setUser: (user) => set({ user })
}));
