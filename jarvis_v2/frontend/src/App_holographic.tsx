import { useState } from 'react';
import { motion } from 'framer-motion';
import './styles/jarvis-theme.css';

interface Action {
  id: string;
  message: string;
  type: 'user' | 'autonomous';
  timestamp: string;
}

interface Memory {
  id: string;
  title: string;
  time: string;
  type: 'live' | 'reminder' | 'analysis';
}

function App() {
  const [actions, setActions] = useState<Action[]>([
    { id: '1', message: 'OPENING WEB BROWSER...', type: 'user', timestamp: new Date().toLocaleTimeString() },
    { id: '2', message: 'USER COMMAND: "SEARCH FOR LATEST NEWS"', type: 'user', timestamp: new Date().toLocaleTimeString() },
    { id: '3', message: 'CALCULATING ROUTE TO OFFICE...', type: 'user', timestamp: new Date().toLocaleTimeString() },
    { id: '4', message: 'AUTONOMOUS: OPTIMIZING SYSTEM PERFORMANCE', type: 'autonomous', timestamp: new Date().toLocaleTimeString() },
  ]);

  const [memories] = useState<Memory[]>([
    { id: '1', title: 'MEETING AT 3:00 PM', time: '', type: 'live' },
    { id: '2', title: 'REMINDER: SEND PROJECT REPORT', time: '', type: 'reminder' },
    { id: '3', title: 'LONG-TERM MEMORY ANALYSIS COMPLETE', time: '', type: 'analysis' },
  ]);

  const [command, setCommand] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [cpuUsage] = useState(36);
  const [ramUsage] = useState(48);
  const [freeSpace] = useState(128);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (command.trim()) {
      setIsProcessing(true);
      const newAction: Action = {
        id: Date.now().toString(),
        message: `USER COMMAND: "${command.toUpperCase()}"`,
        type: 'user',
        timestamp: new Date().toLocaleTimeString()
      };
      setActions(prev => [...prev, newAction]);
      setCommand('');
      
      setTimeout(() => {
        setIsProcessing(false);
        const response: Action = {
          id: (Date.now() + 1).toString(),
          message: `PROCESSING: ${command.toUpperCase()}...`,
          type: 'autonomous',
          timestamp: new Date().toLocaleTimeString()
        };
        setActions(prev => [...prev, response]);
      }, 1500);
    }
  };

  return (
    <div className="relative w-full h-screen bg-black overflow-hidden">
      {/* Hexagonal Grid Background */}
      <div className="absolute inset-0 hex-grid opacity-30" />
      
      {/* Scan Lines */}
      <div className="scan-line" style={{ animationDelay: '0s' }} />
      <div className="scan-line" style={{ animationDelay: '1s' }} />
      
      {/* Particles */}
      {[...Array(20)].map((_, i) => (
        <div
          key={i}
          className="particle"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 4}s`
          }}
        />
      ))}

      {/* Top Border Lines */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-orange-400 to-transparent" />

      {/* Main Container */}
      <div className="relative w-full h-full p-4 flex flex-col">
        
        {/* Top Section - Logo & System Status */}
        <motion.div
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="flex items-center justify-between mb-4"
        >
          {/* Logo */}
          <div className="flex items-center gap-4">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 10, repeat: Infinity, ease: 'linear' }}
              className="relative w-20 h-20"
            >
              <div className="absolute inset-0 rounded-full border-2 border-cyan-400" style={{ boxShadow: '0 0 30px rgba(0,255,255,0.8)' }} />
              <div className="absolute inset-2 rounded-full border-2 border-cyan-400 opacity-50" />
              <div className="absolute inset-4 rounded-full bg-cyan-400" style={{ boxShadow: '0 0 40px rgba(0,255,255,1)' }} />
            </motion.div>
            <div>
              <h1 className="text-4xl font-bold text-cyan-400 tracking-wider glitch" style={{ textShadow: '0 0 20px rgba(0,255,255,0.8)' }}>
                J.A.R.V.I.S.
              </h1>
            </div>
          </div>

          {/* System Status */}
          <div className="hex-panel px-6 py-4">
            <div className="corner-decoration top-left" />
            <div className="corner-decoration top-right" />
            <h3 className="text-cyan-400 text-sm mb-3 tracking-wider">SYSTEM STATUS</h3>
            <div className="flex gap-6">
              {/* CPU */}
              <div className="text-center">
                <div className="relative w-16 h-16 mb-2">
                  <svg className="transform -rotate-90 w-16 h-16">
                    <circle cx="32" cy="32" r="28" stroke="rgba(0,255,255,0.2)" strokeWidth="4" fill="none" />
                    <circle
                      cx="32" cy="32" r="28"
                      stroke="url(#gradient-cpu)"
                      strokeWidth="4"
                      fill="none"
                      strokeDasharray={`${2 * Math.PI * 28}`}
                      strokeDashoffset={`${2 * Math.PI * 28 * (1 - cpuUsage / 100)}`}
                      style={{ filter: 'drop-shadow(0 0 10px rgba(0,255,255,0.8))' }}
                    />
                    <defs>
                      <linearGradient id="gradient-cpu">
                        <stop offset="0%" stopColor="#00ffff" />
                        <stop offset="100%" stopColor="#ff8800" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-cyan-400 font-bold">{cpuUsage}%</span>
                  </div>
                </div>
                <span className="text-cyan-400 text-xs">CPU</span>
              </div>

              {/* RAM */}
              <div className="text-center">
                <div className="relative w-16 h-16 mb-2">
                  <svg className="transform -rotate-90 w-16 h-16">
                    <circle cx="32" cy="32" r="28" stroke="rgba(0,255,255,0.2)" strokeWidth="4" fill="none" />
                    <circle
                      cx="32" cy="32" r="28"
                      stroke="url(#gradient-ram)"
                      strokeWidth="4"
                      fill="none"
                      strokeDasharray={`${2 * Math.PI * 28}`}
                      strokeDashoffset={`${2 * Math.PI * 28 * (1 - ramUsage / 100)}`}
                      style={{ filter: 'drop-shadow(0 0 10px rgba(0,255,255,0.8))' }}
                    />
                    <defs>
                      <linearGradient id="gradient-ram">
                        <stop offset="0%" stopColor="#00ffff" />
                        <stop offset="100%" stopColor="#0080ff" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-cyan-400 font-bold">{ramUsage}%</span>
                  </div>
                </div>
                <span className="text-cyan-400 text-xs">RAM</span>
              </div>

              {/* FREE */}
              <div className="text-center">
                <div className="relative w-16 h-16 mb-2">
                  <svg className="transform -rotate-90 w-16 h-16">
                    <circle cx="32" cy="32" r="28" stroke="rgba(0,255,255,0.2)" strokeWidth="4" fill="none" />
                    <circle
                      cx="32" cy="32" r="28"
                      stroke="#00ffff"
                      strokeWidth="4"
                      fill="none"
                      strokeDasharray={`${2 * Math.PI * 28}`}
                      strokeDashoffset={`${2 * Math.PI * 28 * 0.3}`}
                      style={{ filter: 'drop-shadow(0 0 10px rgba(0,255,255,0.8))' }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center flex-col">
                    <span className="text-cyan-400 font-bold text-sm">{freeSpace}</span>
                    <span className="text-cyan-400 text-[8px]">GB</span>
                  </div>
                </div>
                <span className="text-cyan-400 text-xs">FREE</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Main Content Area */}
        <div className="flex-1 flex gap-4 mb-4">
          
          {/* Left Panel - Action Log */}
          <motion.div
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="w-1/4 hex-panel p-4 relative overflow-hidden"
          >
            <div className="corner-decoration top-left" />
            <div className="corner-decoration bottom-left" />
            
            <div className="flex items-center gap-2 mb-4">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-cyan-400 animate-pulse" style={{ boxShadow: '0 0 10px rgba(0,255,255,1)' }} />
                <div className="w-2 h-2 bg-cyan-400 animate-pulse" style={{ animationDelay: '0.2s', boxShadow: '0 0 10px rgba(0,255,255,1)' }} />
                <div className="w-2 h-2 bg-cyan-400 animate-pulse" style={{ animationDelay: '0.4s', boxShadow: '0 0 10px rgba(0,255,255,1)' }} />
              </div>
              <h3 className="text-cyan-400 text-sm tracking-wider">ACTION LOG</h3>
            </div>

            <div className="space-y-2 custom-scrollbar overflow-y-auto max-h-[calc(100vh-300px)]">
              {actions.map((action, idx) => (
                <motion.div
                  key={action.id}
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: idx * 0.1 }}
                  className={`p-3 border-l-2 ${
                    action.type === 'user' ? 'border-cyan-400 bg-cyan-900/20' : 'border-orange-400 bg-orange-900/20'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <div className={`w-2 h-2 mt-1 rounded-full ${
                      action.type === 'user' ? 'bg-cyan-400' : 'bg-orange-400'
                    }`} style={{ boxShadow: action.type === 'user' ? '0 0 10px rgba(0,255,255,1)' : '0 0 10px rgba(255,136,0,1)' }} />
                    <div className="flex-1">
                      <p className={`text-xs font-mono ${action.type === 'user' ? 'text-cyan-300' : 'text-orange-300'}`}>
                        {action.message}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="absolute bottom-4 left-4 right-4 flex items-center gap-2 text-cyan-400 text-xs">
              <div className="status-dot" />
              <span className="data-stream">CONNECTED - AI ONLINE</span>
            </div>
          </motion.div>

          {/* Center - Holographic Display */}
          <div className="flex-1 relative flex items-center justify-center">
            <motion.div
              animate={{ rotateY: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
              className="relative w-96 h-96"
              style={{ transformStyle: 'preserve-3d' }}
            >
              {/* Rotating Rings */}
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="rotating-ring"
                  style={{
                    width: `${300 - i * 40}px`,
                    height: `${300 - i * 40}px`,
                    top: `${50 + i * 20}px`,
                    left: `${50 + i * 20}px`,
                    animationDelay: `${i * 0.5}s`,
                    boxShadow: '0 0 20px rgba(0,255,255,0.5)'
                  }}
                />
              ))}

              {/* Center Orb */}
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="w-32 h-32 rounded-full bg-gradient-to-br from-cyan-400 to-blue-600"
                  style={{ boxShadow: '0 0 60px rgba(0,255,255,1), inset 0 0 40px rgba(0,255,255,0.5)' }}
                />
              </div>

              {/* Pulse Rings */}
              {[...Array(3)].map((_, i) => (
                <div
                  key={`pulse-${i}`}
                  className="pulse-ring"
                  style={{
                    width: '200px',
                    height: '200px',
                    top: '100px',
                    left: '100px',
                    animationDelay: `${i * 0.7}s`
                  }}
                />
              ))}
            </motion.div>
          </div>

          {/* Right Panel - Memory & Tasks */}
          <motion.div
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="w-1/4 hex-panel-orange p-4 relative"
          >
            <div className="corner-decoration top-right" style={{ borderColor: 'var(--primary-orange)' }} />
            <div className="corner-decoration bottom-right" style={{ borderColor: 'var(--primary-orange)' }} />
            
            <div className="flex items-center gap-2 mb-4">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-orange-400 animate-pulse" style={{ boxShadow: '0 0 10px rgba(255,136,0,1)' }} />
                <div className="w-2 h-2 bg-orange-400 animate-pulse" style={{ animationDelay: '0.2s', boxShadow: '0 0 10px rgba(255,136,0,1)' }} />
                <div className="w-2 h-2 bg-orange-400 animate-pulse" style={{ animationDelay: '0.4s', boxShadow: '0 0 10px rgba(255,136,0,1)' }} />
              </div>
              <h3 className="text-orange-400 text-sm tracking-wider">MEMORY & TASKS</h3>
            </div>

            <div className="space-y-3">
              {memories.map((memory, idx) => (
                <motion.div
                  key={memory.id}
                  initial={{ x: 20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: idx * 0.1 }}
                  className="p-3 border border-orange-400/30 bg-orange-900/10 relative overflow-hidden"
                >
                  <div className="circuit-line top-0" style={{ animationDelay: `${idx * 0.3}s` }} />
                  <div className="flex items-start gap-2">
                    <div className="text-orange-400 text-lg">
                      {memory.type === 'live' && '🔴'}
                      {memory.type === 'reminder' && '📋'}
                      {memory.type === 'analysis' && '🧠'}
                    </div>
                    <div className="flex-1">
                      <p className="text-orange-300 text-xs font-mono">{memory.title}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Bottom - Command Input */}
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="relative"
        >
          <div className="hex-panel p-4">
            <div className="corner-decoration bottom-left" />
            <div className="corner-decoration bottom-right" />
            
            <form onSubmit={handleSubmit} className="flex items-center gap-4">
              {/* Processing Indicator */}
              <div className="flex items-center gap-2">
                {isProcessing ? (
                  <>
                    <div className="data-stream text-cyan-400 text-xs">PROCESSING...</div>
                    <div className="flex gap-1">
                      {[...Array(10)].map((_, i) => (
                        <div
                          key={i}
                          className="w-1 bg-cyan-400"
                          style={{
                            height: `${Math.random() * 20 + 10}px`,
                            animation: 'pulse 0.5s ease-in-out infinite',
                            animationDelay: `${i * 0.1}s`
                          }}
                        />
                      ))}
                    </div>
                  </>
                ) : (
                  <div className="w-8 h-8 rounded-full border-2 border-cyan-400 flex items-center justify-center">
                    <div className="w-4 h-4 rounded-full bg-cyan-400" style={{ boxShadow: '0 0 10px rgba(0,255,255,1)' }} />
                  </div>
                )}
              </div>

              {/* Input */}
              <input
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="ENTER COMMAND..."
                className="flex-1 bg-transparent border-b-2 border-cyan-400/50 text-cyan-400 placeholder-cyan-400/30 outline-none px-4 py-2 font-mono text-sm focus:border-cyan-400 transition-colors"
                style={{ textShadow: '0 0 10px rgba(0,255,255,0.5)' }}
              />

              {/* Send Button */}
              <button
                type="submit"
                disabled={!command.trim() || isProcessing}
                className="px-8 py-2 bg-gradient-to-r from-orange-500 to-orange-600 text-white font-bold tracking-wider disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden group"
                style={{
                  clipPath: 'polygon(10px 0%, 100% 0%, calc(100% - 10px) 100%, 0% 100%)',
                  boxShadow: '0 0 20px rgba(255,136,0,0.5)'
                }}
              >
                <span className="relative z-10">SEND</span>
                <div className="absolute inset-0 bg-gradient-to-r from-orange-600 to-orange-700 transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left" />
              </button>
            </form>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

export default App;
