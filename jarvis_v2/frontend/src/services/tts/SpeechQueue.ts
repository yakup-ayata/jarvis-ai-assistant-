// Speech Queue Manager - FIFO with priority support

import { SpeechRequest } from './types';

export class SpeechQueue {
  private queue: SpeechRequest[] = [];
  private isSpeaking: boolean = false;
  private maxQueueSize: number = 5;

  public enqueue(request: SpeechRequest): void {
    // High priority messages interrupt
    if (request.priority === 'high' || request.priority === 'critical') {
      this.clearAndSpeak(request);
      return;
    }

    // Check queue size
    if (this.queue.length >= this.maxQueueSize) {
      // Remove oldest non-critical message
      const index = this.queue.findIndex(
        req => req.priority !== 'critical' && req.priority !== 'high'
      );
      if (index !== -1) {
        const dropped = this.queue.splice(index, 1)[0];
        console.warn('TTS: Queue full, dropped message:', dropped.text);
      }
    }

    this.queue.push(request);

    if (!this.isSpeaking) {
      this.processNext();
    }
  }

  public clearAndSpeak(request: SpeechRequest): void {
    speechSynthesis.cancel();
    this.queue = [];
    this.speakNow(request);
  }

  public clear(): void {
    this.queue = [];
    speechSynthesis.cancel();
    this.isSpeaking = false;
  }

  private processNext(): void {
    if (this.queue.length === 0) {
      this.isSpeaking = false;
      return;
    }

    const request = this.queue.shift()!;
    this.speakNow(request);
  }

  private speakNow(request: SpeechRequest): void {
    const utterance = new SpeechSynthesisUtterance(request.text);
    
    if (request.voice) {
      utterance.voice = request.voice;
    }
    
    utterance.rate = request.rate;
    utterance.pitch = request.pitch;

    utterance.onend = () => {
      this.isSpeaking = false;
      this.processNext();
    };

    utterance.onerror = (event) => {
      console.error('TTS Error:', event);
      this.isSpeaking = false;
      this.processNext();
    };

    this.isSpeaking = true;
    speechSynthesis.speak(utterance);
  }

  public getQueueLength(): number {
    return this.queue.length;
  }

  public isCurrentlySpeaking(): boolean {
    return this.isSpeaking;
  }
}
