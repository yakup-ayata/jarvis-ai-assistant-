import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface SpeechVisualizerProps {
  isSpeaking: boolean;
}

export const SpeechVisualizer: React.FC<SpeechVisualizerProps> = ({ isSpeaking }) => {
  return (
    <div className="fixed inset-0 pointer-events-none z-40">
      <AnimatePresence>
        {isSpeaking && (
          <>
            {/* Circular Wave Effects - Center */}
            <motion.div
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
              initial={{ scale: 0, opacity: 1 }}
              animate={{ scale: 4, opacity: 0 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
            >
              <div className="w-32 h-32 rounded-full border-2 border-cyan-400 shadow-[0_0_30px_rgba(0,255,255,0.6)]" />
            </motion.div>
            
            <motion.div
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
              initial={{ scale: 0, opacity: 1 }}
              animate={{ scale: 4, opacity: 0 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.5, ease: 'easeOut' }}
            >
              <div className="w-32 h-32 rounded-full border-2 border-blue-400 shadow-[0_0_30px_rgba(0,150,255,0.6)]" />
            </motion.div>
            
            <motion.div
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
              initial={{ scale: 0, opacity: 1 }}
              animate={{ scale: 4, opacity: 0 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ duration: 2, repeat: Infinity, delay: 1, ease: 'easeOut' }}
            >
              <div className="w-32 h-32 rounded-full border-2 border-cyan-300 shadow-[0_0_30px_rgba(0,255,255,0.4)]" />
            </motion.div>

            {/* Audio Bars - Bottom Center */}
            <div className="absolute bottom-12 left-1/2 -translate-x-1/2 flex gap-2">
              {[...Array(7)].map((_, i) => (
                <motion.div
                  key={i}
                  className="w-2 bg-gradient-to-t from-cyan-400 to-blue-500 rounded-full shadow-[0_0_10px_rgba(0,255,255,0.8)]"
                  animate={{
                    height: [20, 60, 20],
                  }}
                  transition={{
                    duration: 0.6,
                    repeat: Infinity,
                    delay: i * 0.08,
                    ease: 'easeInOut'
                  }}
                />
              ))}
            </div>

            {/* Pulsing Glow Effect */}
            <motion.div
              className="absolute inset-0 bg-gradient-radial from-cyan-400/10 via-transparent to-transparent"
              animate={{
                opacity: [0.1, 0.3, 0.1],
                scale: [1, 1.05, 1],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeInOut'
              }}
            />

            {/* Corner Accents */}
            <motion.div
              className="absolute top-8 left-8 w-16 h-16 border-l-2 border-t-2 border-cyan-400"
              animate={{
                opacity: [0.3, 1, 0.3],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
              }}
            />
            
            <motion.div
              className="absolute top-8 right-8 w-16 h-16 border-r-2 border-t-2 border-cyan-400"
              animate={{
                opacity: [0.3, 1, 0.3],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: 0.3,
              }}
            />
            
            <motion.div
              className="absolute bottom-8 left-8 w-16 h-16 border-l-2 border-b-2 border-cyan-400"
              animate={{
                opacity: [0.3, 1, 0.3],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: 0.6,
              }}
            />
            
            <motion.div
              className="absolute bottom-8 right-8 w-16 h-16 border-r-2 border-b-2 border-cyan-400"
              animate={{
                opacity: [0.3, 1, 0.3],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: 0.9,
              }}
            />

            {/* Scanning Line Effect */}
            <motion.div
              className="absolute left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_20px_rgba(0,255,255,0.8)]"
              animate={{
                top: ['0%', '100%'],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: 'linear',
              }}
            />

            {/* Orbital Rings */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
              <motion.div
                className="w-64 h-64"
                animate={{ rotate: 360 }}
                transition={{ duration: 10, repeat: Infinity, ease: 'linear' }}
              >
                <svg viewBox="0 0 100 100" className="w-full h-full">
                  <circle
                    cx="50"
                    cy="50"
                    r="45"
                    stroke="rgba(0, 212, 255, 0.3)"
                    strokeWidth="0.5"
                    fill="none"
                    strokeDasharray="5,5"
                  />
                </svg>
              </motion.div>
            </div>

            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
              <motion.div
                className="w-80 h-80"
                animate={{ rotate: -360 }}
                transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
              >
                <svg viewBox="0 0 100 100" className="w-full h-full">
                  <circle
                    cx="50"
                    cy="50"
                    r="48"
                    stroke="rgba(0, 150, 255, 0.2)"
                    strokeWidth="0.5"
                    fill="none"
                    strokeDasharray="3,7"
                  />
                </svg>
              </motion.div>
            </div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
