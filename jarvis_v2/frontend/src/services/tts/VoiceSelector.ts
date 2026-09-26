// Voice Selection Service - Prefers Apple Daniel

import { Language } from './types';

export class VoiceSelector {
  private voices: SpeechSynthesisVoice[] = [];
  private selectedVoice: SpeechSynthesisVoice | null = null;

  public initialize(): void {
    this.voices = speechSynthesis.getVoices();
    this.selectDefaultVoice();
  }

  private selectDefaultVoice(): void {
    // Try to find Apple Daniel
    const daniel = this.voices.find(
      voice => voice.name === 'Daniel' && voice.lang.startsWith('en')
    );

    if (daniel) {
      this.selectedVoice = daniel;
      console.log('TTS: Using Apple Daniel voice');
      return;
    }

    // Fallback to first English voice
    const englishVoice = this.voices.find(voice => 
      voice.lang.startsWith('en')
    );

    this.selectedVoice = englishVoice || this.voices[0] || null;
    
    if (this.selectedVoice) {
      console.log(`TTS: Using fallback voice: ${this.selectedVoice.name}`);
    } else {
      console.warn('TTS: No voices available');
    }
  }

  public selectVoice(language: Language): SpeechSynthesisVoice | null {
    if (language === 'tr') {
      const turkishVoice = this.voices.find(voice => 
        voice.lang.startsWith('tr')
      );
      return turkishVoice || this.selectedVoice;
    }

    return this.selectedVoice;
  }

  public getAvailableVoices(): SpeechSynthesisVoice[] {
    return this.voices;
  }
}
