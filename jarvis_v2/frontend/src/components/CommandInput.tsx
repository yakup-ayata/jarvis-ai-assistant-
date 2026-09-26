import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SystemState } from '../hooks/useWebSocket';

interface CommandInputProps {
  onSubmit: (command: string) => void;
  isProcessing?: boolean;
  isSpeaking?: boolean;
  onInterrupt?: () => void;
  systemState?: SystemState;
}

// Durum → buton rengi
const STATE_BUTTON: Record<string, { bg: string; shadow: string; label: string; icon: string }> = {
  idle:      { bg: 'from-cyan-500 to-blue-600',    shadow: 'rgba(0,212,255,0.4)',  label: 'Konuş',        icon: '🎙️' },
  listening: { bg: 'from-red-500 to-red-600',      shadow: 'rgba(255,0,0,0.6)',    label: 'Dinliyorum...', icon: '🎤' },
  thinking:  { bg: 'from-yellow-500 to-amber-600', shadow: 'rgba(250,204,21,0.5)', label: 'Düşünüyor...',  icon: '⏳' },
  acting:    { bg: 'from-green-500 to-emerald-600',shadow: 'rgba(34,197,94,0.5)',  label: 'Çalışıyor...',  icon: '⚙️' },
  speaking:  { bg: 'from-purple-500 to-violet-600',shadow: 'rgba(168,85,247,0.5)', label: 'Konuşuyor...',  icon: '🔊' },
};

export const CommandInput: React.FC<CommandInputProps> = ({
  onSubmit,
  isProcessing = false,
  isSpeaking = false,
  onInterrupt,
  systemState = 'idle',
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript]   = useState('');
  const recognitionRef = useRef<any>(null);
  const isRecordingRef = useRef(false);  // sync ref for callbacks

  // ── Speech Recognition init ──────────────────────────────────────────────────
  useEffect(() => {
    const SR = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (!SR) {
      console.error('❌ Speech recognition not supported');
      return;
    }

    const recognition = new SR();
    recognition.continuous    = false;
    recognition.interimResults = true;
    recognition.lang           = 'tr-TR';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      isRecordingRef.current = true;
      setIsRecording(true);
      setTranscript('Dinliyorum...');
    };

    recognition.onresult = (event: any) => {
      const result     = event.results[event.results.length - 1];
      const text       = result[0].transcript;
      const isFinal    = result.isFinal;

      if (isFinal) {
        setTranscript(text);
        setIsRecording(false);
        isRecordingRef.current = false;

        // Interrupt JARVIS if speaking, then send command
        if (isSpeaking && onInterrupt) onInterrupt();
        if (text.trim()) onSubmit(text.trim());
        setTimeout(() => setTranscript(''), 1500);
      } else {
        setTranscript(text + '...');
      }
    };

    recognition.onerror = (event: any) => {
      console.error('❌ Speech error:', event.error);
      setIsRecording(false);
      isRecordingRef.current = false;
      setTranscript('');
    };

    recognition.onend = () => {
      setIsRecording(false);
      isRecordingRef.current = false;
    };

    recognitionRef.current = recognition;
  }, [onSubmit, isSpeaking, onInterrupt]);

  // ── Toggle mic ───────────────────────────────────────────────────────────────
  const handleMicClick = useCallback(() => {
    if (!recognitionRef.current) return;

    if (isRecordingRef.current) {
      recognitionRef.current.stop();
    } else {
      // If JARVIS is speaking, interrupt first
      if (isSpeaking && onInterrupt) onInterrupt();
      try {
        recognitionRef.current.start();
      } catch (e) {
        console.error('Mic start error:', e);
      }
    }
  }, [isSpeaking, onInterrupt]);

  // ── Derive button state ───────────────────────────────────────────────────────
  const btnKey = isRecording ? 'listening'
               : isSpeaking  ? 'speaking'
               : systemState === 'thinking' ? 'thinking'
               : systemState === 'acting'   ? 'acting'
               : 'idle';
  const btn = STATE_BUTTON[btnKey];

  return (
    <motion.div
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="fixed bottom-8 left-1/2 -translate-x-1/2 w-full max-w-md px-4 z-50"
    >
      <div className="relative">
        {/* Glow halo */}
        <AnimatePresence>
          {(isRecording || isSpeaking) && (
            <motion.div
              key="halo"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 0.4, scale: 1 }}
              exit={{ opacity: 0 }}
              className={`absolute inset-0 rounded-full blur-2xl bg-gradient-to-r ${btn.bg}`}
            />
          )}
        </AnimatePresence>

        {/* Container */}
        <div className="relative bg-black/70 backdrop-blur-md rounded-full border border-white/10 shadow-lg overflow-hidden">
          <div className="p-2">
            <motion.button
              type="button"
              onClick={handleMicClick}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className={`w-full h-16 rounded-full flex items-center justify-center gap-3 bg-gradient-to-r ${btn.bg} transition-all duration-300`}
              style={{ boxShadow: `0 0 30px ${btn.shadow}` }}
            >
              <motion.span
                animate={isRecording ? { scale: [1, 1.3, 1], opacity: [1, 0.5, 1] } : {}}
                transition={{ duration: 0.8, repeat: Infinity }}
                className="text-3xl"
              >
                {btn.icon}
              </motion.span>
              <span className="text-white text-lg font-medium">{btn.label}</span>
            </motion.button>
          </div>
        </div>

        {/* Transcript bubble */}
        <AnimatePresence>
          {transcript && (
            <motion.div
              key="transcript"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -5 }}
              className="absolute -top-16 left-1/2 -translate-x-1/2 bg-black/90 backdrop-blur px-6 py-3 rounded-full border border-cyan-500/30 max-w-xs whitespace-nowrap overflow-hidden text-ellipsis"
            >
              <span className="text-sm text-cyan-400 font-medium">{transcript}</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Processing spinner */}
        <AnimatePresence>
          {isProcessing && !isRecording && !transcript && (
            <motion.div
              key="spinner"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="absolute -top-16 left-1/2 -translate-x-1/2 bg-black/90 backdrop-blur px-6 py-3 rounded-full border border-yellow-500/30 flex items-center gap-3"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-4 h-4 border-2 border-yellow-400 border-t-transparent rounded-full"
              />
              <span className="text-sm text-yellow-400 font-medium">JARVIS düşünüyor...</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};
