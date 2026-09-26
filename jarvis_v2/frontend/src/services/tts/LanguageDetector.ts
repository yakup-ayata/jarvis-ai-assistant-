// Language Detection Service

import { Language } from './types';

export class LanguageDetector {
  private turkishChars = /[çğıöşüÇĞİÖŞÜ]/;

  public detect(text: string): Language {
    return this.turkishChars.test(text) ? 'tr' : 'en';
  }
}
