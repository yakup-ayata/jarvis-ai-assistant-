// Main TTS Service - Singleton pattern

import { SpeechOptions, SpeechRequest } from './types';
import { VoiceSelector } from './VoiceSelector';
import { SpeechQueue } from './SpeechQueue';
import { LanguageDetector } from './LanguageDetector';
import { SettingsManager } from './SettingsManager';

export class TTSService {
  private static instance: TTSService;
  private enabled: boolean = false;
  private voiceSelector: VoiceSelector;
  private speechQueue: SpeechQueue;
  private languageDetector: LanguageDetector;
  private settingsManager: SettingsManager;

  private constructor() {
    this.voiceSelector = new VoiceSelector();
    this.speechQueue = new SpeechQueue();
    this.languageDetector = new LanguageDetector();
    this.settingsManager = new SettingsManager();
    this.initialize();
  }

  public static getInstance(): TTSService {
    if (!TTSService.instance) {
      TTSService.instance = new TTSService();
    }
    return TTSService.instance;
  }

  private initialize(): void {
    // Check API availability
    if (!('speechSynthesis' in window)) {
      console.warn('TTS: Speech Synthesis API not supported');
      return;
    }

    // Load settings
    this.enabled = this.settingsManager.getTTSEnabled();

    // Initialize voice selector
    this.voiceSelector.initialize();

    // Listen for voice list changes
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = () => {
        this.voiceSelector.initialize();
      };
    }

    console.log(`TTS: Initialized (enabled: ${this.enabled})`);
  }

  public speak(text: string, options?: SpeechOptions): void {
    if (!this.enabled || !this.isSupported()) return;

    const language = this.languageDetector.detect(text);
    const voice = this.voiceSelector.selectVoice(language);
    
    const request: SpeechRequest = {
      text,
      voice,
      priority: options?.priority || 'normal',
      rate: options?.rate || 1.0,
      pitch: options?.pitch || 1.0,
    };

    if (options?.interrupt) {
      this.speechQueue.clearAndSpeak(request);
    } else {
      this.speechQueue.enqueue(request);
    }
  }

  public setEnabled(enabled: boolean): void {
    this.enabled = enabled;
    this.settingsManager.setTTSEnabled(enabled);
    
    if (!enabled) {
      this.stop();
    }

    console.log(`TTS: ${enabled ? 'Enabled' : 'Disabled'}`);
  }

  public isEnabled(): boolean {
    return this.enabled;
  }

  public isSupported(): boolean {
    return 'speechSynthesis' in window;
  }

  public stop(): void {
    speechSynthesis.cancel();
    this.speechQueue.clear();
  }

  public getStatus(): {
    enabled: boolean;
    supported: boolean;
    queueLength: number;
    speaking: boolean;
  } {
    return {
      enabled: this.enabled,
      supported: this.isSupported(),
      queueLength: this.speechQueue.getQueueLength(),
      speaking: this.speechQueue.isCurrentlySpeaking()
    };
  }
}
