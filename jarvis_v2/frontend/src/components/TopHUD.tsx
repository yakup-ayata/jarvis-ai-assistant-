import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface SystemStats {
  cpu: number;
  memory: number;
  daemonStatus: 'running' | 'stopped' | 'unknown';
}

interface TopHUDProps {
  ttsEnabled: boolean;
  ttsSupported: boolean;
  onTTSToggle: () => void;
}

export const TopHUD: React.FC<TopHUDProps> = ({ 
  ttsEnabled, 
  ttsSupported, 
  onTTSToggle 
}) => {
  const [stats, setStats] = useState<SystemStats>({
    cpu: 0,
    memory: 0,
    daemonStatus: 'unknown'
  });

  useEffect(() => {
    // Simulate system stats (will be replaced with real WebSocket data)
    const interval = setInterval(() => {
      setStats({
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        daemonStatus: 'running'
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-400';
      case 'stopped': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getBarColor = (value: number) => {
    if (value > 80) return 'from-red-500 to-red-600';
    if (value > 60) return 'from-yellow-500 to-yellow-600';
    return 'from-cyan-500 to-blue-600';
  };

  return (
    <motion.div
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="fixed top-0 left-0 right-0 z-50 bg-black bg-opacity-80 backdrop-blur-md border-b border-cyan-500/30 shadow-[0_0_20px_rgba(0,255,255,0.3)]"
    >
      <div className="container mx-auto px-6 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring' }}
            className="flex items-center gap-3"
          >
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-[0_0_20px_rgba(0,255,255,0.5)]">
              <span className="text-white font-bold text-xl">J</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                JARVIS
              </h1>
              <p className="text-xs text-gray-400">Hybrid AI OS</p>
            </div>
          </motion.div>

          {/* System Stats */}
          <div className="flex items-center gap-6">
            {/* CPU */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="flex flex-col gap-1"
            >
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 uppercase tracking-wider">CPU</span>
                <span className="text-sm font-mono text-cyan-400">{stats.cpu.toFixed(1)}%</span>
              </div>
              <div className="w-32 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${stats.cpu}%` }}
                  transition={{ duration: 0.5 }}
                  className={`h-full bg-gradient-to-r ${getBarColor(stats.cpu)} shadow-[0_0_10px_rgba(0,255,255,0.5)]`}
                />
              </div>
            </motion.div>

            {/* Memory */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="flex flex-col gap-1"
            >
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 uppercase tracking-wider">RAM</span>
                <span className="text-sm font-mono text-cyan-400">{stats.memory.toFixed(1)}%</span>
              </div>
              <div className="w-32 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${stats.memory}%` }}
                  transition={{ duration: 0.5 }}
                  className={`h-full bg-gradient-to-r ${getBarColor(stats.memory)} shadow-[0_0_10px_rgba(0,255,255,0.5)]`}
                />
              </div>
            </motion.div>

            {/* Daemon Status */}
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5, type: 'spring' }}
              className="flex items-center gap-2 px-4 py-2 bg-gray-900 rounded-lg border border-gray-700"
            >
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [1, 0.5, 1]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'easeInOut'
                }}
                className={`w-2 h-2 rounded-full ${
                  stats.daemonStatus === 'running' ? 'bg-green-400 shadow-[0_0_10px_rgba(0,255,0,0.8)]' : 'bg-red-400'
                }`}
              />
              <span className={`text-sm font-medium ${getStatusColor(stats.daemonStatus)}`}>
                {stats.daemonStatus === 'running' ? 'ONLINE' : 'OFFLINE'}
              </span>
            </motion.div>

            {/* TTS Toggle Button */}
            <motion.button
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6, type: 'spring' }}
              onClick={onTTSToggle}
              disabled={!ttsSupported}
              className={`flex items-center gap-2 px-4 py-2 bg-gray-900 rounded-lg border transition-all ${
                ttsSupported 
                  ? 'border-gray-700 hover:border-cyan-500/50 cursor-pointer hover:shadow-[0_0_15px_rgba(0,255,255,0.3)]' 
                  : 'border-gray-800 opacity-50 cursor-not-allowed'
              }`}
              title={
                !ttsSupported 
                  ? 'TTS not supported in this browser' 
                  : ttsEnabled 
                    ? 'Frontend TTS: ON (Fallback mode)\nBackend TTS: Primary (Daniel voice)' 
                    : 'Frontend TTS: OFF\nBackend TTS: Primary (Daniel voice)'
              }
              aria-label={ttsEnabled ? 'Disable TTS' : 'Enable TTS'}
            >
              {ttsEnabled ? (
                <>
                  {/* Speaker with sound waves */}
                  <motion.div
                    animate={{
                      scale: [1, 1.1, 1],
                    }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      ease: 'easeInOut'
                    }}
                    className="relative"
                  >
                    <svg 
                      className="w-5 h-5 text-cyan-400" 
                      fill="currentColor" 
                      viewBox="0 0 20 20"
                    >
                      <path 
                        fillRule="evenodd" 
                        d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" 
                        clipRule="evenodd" 
                      />
                    </svg>
                  </motion.div>
                  <span className="text-sm font-medium text-cyan-400">TTS</span>
                </>
              ) : (
                <>
                  {/* Muted speaker */}
                  <svg 
                    className="w-5 h-5 text-gray-500" 
                    fill="currentColor" 
                    viewBox="0 0 20 20"
                  >
                    <path 
                      fillRule="evenodd" 
                      d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM12.293 7.293a1 1 0 011.414 0L15 8.586l1.293-1.293a1 1 0 111.414 1.414L16.414 10l1.293 1.293a1 1 0 01-1.414 1.414L15 11.414l-1.293 1.293a1 1 0 01-1.414-1.414L13.586 10l-1.293-1.293a1 1 0 010-1.414z" 
                      clipRule="evenodd" 
                    />
                  </svg>
                  <span className="text-sm font-medium text-gray-500">TTS</span>
                </>
              )}
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
