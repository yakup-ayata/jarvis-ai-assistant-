import { useEffect, useRef, useState } from 'react';

interface UseWakeWordOptions {
  wakeWords?: string[];
  onWakeWordDetected?: () => void;
  enabled?: boolean;
}

/**
 * Hook for continuous wake word detection
 * Listens for "Jarvis", "Hey Jarvis", "OK Jarvis" etc.
 */
export const useWakeWord = ({
  wakeWords = ['jarvis', 'hey jarvis', 'ok jarvis', 'hello jarvis'],
  onWakeWordDetected,
  enabled = false
}: UseWakeWordOptions = {}) => {
  const [isListening, setIsListening] = useState(false);
  const [lastDetection, setLastDetection] = useState<Date | null>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Initialize Speech Recognition
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.warn('Speech Recognition not supported');
      return;
    }

    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = true;
    recognitionRef.current.interimResults = true;
    recognitionRef.current.lang = 'en-US';

    recognitionRef.current.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0].transcript)
        .join('')
        .toLowerCase()
        .trim();

      console.log('Wake word detection:', transcript);

      // Check for wake words
      for (const wakeWord of wakeWords) {
        if (transcript.includes(wakeWord.toLowerCase())) {
          console.log('✓ Wake word detected:', wakeWord);
          setLastDetection(new Date());
          
          if (onWakeWordDetected) {
            onWakeWordDetected();
          }
          
          // Stop and restart to clear buffer
          if (recognitionRef.current) {
            recognitionRef.current.stop();
            setTimeout(() => {
              if (recognitionRef.current && enabled) {
                try {
                  recognitionRef.current.start();
                } catch (e) {
                  // Already started
                }
              }
            }, 500);
          }
          
          break;
        }
      }
    };

    recognitionRef.current.onerror = (event: any) => {
      console.error('Wake word detection error:', event.error);
      
      // Restart on error (except if aborted)
      if (event.error !== 'aborted' && enabled) {
        setTimeout(() => {
          if (recognitionRef.current && enabled) {
            try {
              recognitionRef.current.start();
            } catch (e) {
              // Already started
            }
          }
        }, 1000);
      }
    };

    recognitionRef.current.onend = () => {
      // Auto-restart if still enabled
      if (enabled) {
        setTimeout(() => {
          if (recognitionRef.current && enabled) {
            try {
              recognitionRef.current.start();
              console.log('Wake word detection restarted');
            } catch (e) {
              // Already started
            }
          }
        }, 500);
      }
    };

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [wakeWords, onWakeWordDetected]);

  useEffect(() => {
    if (!recognitionRef.current) return;

    if (enabled && !isListening) {
      try {
        recognitionRef.current.start();
        setIsListening(true);
        console.log('🎙️  Wake word detection started');
      } catch (error) {
        console.error('Failed to start wake word detection:', error);
      }
    } else if (!enabled && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      console.log('🛑 Wake word detection stopped');
    }
  }, [enabled, isListening]);

  const start = () => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (error) {
        console.error('Failed to start wake word detection:', error);
      }
    }
  };

  const stop = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  return {
    isListening,
    lastDetection,
    start,
    stop
  };
};
