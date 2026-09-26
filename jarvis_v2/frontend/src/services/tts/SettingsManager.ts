// TTS Settings Manager with localStorage persistence

export class SettingsManager {
  private readonly STORAGE_KEY = 'jarvis_tts_enabled';

  public getTTSEnabled(): boolean {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      return stored === 'true';
    } catch (error) {
      console.error('TTS: Failed to read settings', error);
      return false;
    }
  }

  public setTTSEnabled(enabled: boolean): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, enabled.toString());
    } catch (error) {
      console.error('TTS: Failed to save settings', error);
    }
  }
}
