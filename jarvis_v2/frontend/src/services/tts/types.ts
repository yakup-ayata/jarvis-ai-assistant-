// TTS Type Definitions

export interface SpeechOptions {
  priority?: 'low' | 'normal' | 'high' | 'critical';
  interrupt?: boolean;
  rate?: number;
  pitch?: number;
}

export interface SpeechRequest {
  text: string;
  voice: SpeechSynthesisVoice | null;
  priority: 'low' | 'normal' | 'high' | 'critical';
  rate: number;
  pitch: number;
}

export type Language = 'en' | 'tr';
