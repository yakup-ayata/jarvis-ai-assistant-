import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useWebSocket, SystemState } from './hooks/useWebSocket';
import { TopHUD } from './components/TopHUD';
import { SpeechVisualizer } from './components/SpeechVisualizer';
import { CommandInput } from './components/CommandInput';
import './styles/jarvis-theme.css';

// ── Types ──────────────────────────────────────────────────────────────────────
interface Action {
  id: string;
  message: string;
  type: 'user' | 'system' | 'autonomous' | 'chat';
  timestamp: string;
}

interface Memory {
  id: string;
  type: 'reflection' | 'goal' | 'analysis';
  title: string;
  content: string;
  priority?: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
}

interface SystemMetric {
  label: string;
  value: number;
  unit: string;
}

// ── Ring color per system state ────────────────────────────────────────────────
const STATE_COLORS: Record<SystemState, { ring: string; glow: string; label: string }> = {
  idle:      { ring: 'rgba(0,212,255,0.4)',   glow: 'rgba(0,212,255,0.2)',   label: 'HAZIR'      },
  listening: { ring: 'rgba(0,212,255,0.9)',   glow: 'rgba(0,212,255,0.5)',   label: 'DİNLİYOR'   },
  thinking:  { ring: 'rgba(250,204,21,0.8)',  glow: 'rgba(250,204,21,0.4)',  label: 'DÜŞÜNÜYOR'  },
  acting:    { ring: 'rgba(34,197,94,0.8)',   glow: 'rgba(34,197,94,0.4)',   label: 'ÇALIŞIYOR'  },
};

// ── App ────────────────────────────────────────────────────────────────────────
function App() {
  const { isConnected, sendMessage, lastMessage, systemState, interruptSpeech, isSpeaking } =
    useWebSocket('ws://localhost:8001/ws');

  const [actions, setActions] = useState<Action[]>([
    { id: '1', message: 'Sistem başlatıldı', type: 'system', timestamp: new Date().toLocaleTimeString() },
    { id: '2', message: 'Backend bağlantısı bekleniyor...', type: 'system', timestamp: new Date().toLocaleTimeString() },
  ]);
  const [memories, setMemories]   = useState<Memory[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [chatBuffer, setChatBuffer] = useState('');   // streaming chat text
  const [metrics, setMetrics] = useState<SystemMetric[]>([
    { label: 'CPU',  value: 0,  unit: '%' },
    { label: 'RAM',  value: 0,  unit: '%' },
    { label: 'DISK', value: 0,  unit: '%' },
  ]);

  const actionsEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll activity log
  useEffect(() => {
    actionsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [actions]);

  // ── Connection state ─────────────────────────────────────────────────────────
  useEffect(() => {
    setActions(prev => [...prev, {
      id: Date.now().toString(),
      message: isConnected ? 'Backend bağlandı ✓' : 'Backend bağlantısı kesildi',
      type: 'system',
      timestamp: new Date().toLocaleTimeString(),
    }]);
  }, [isConnected]);

  // ── isProcessing sync with systemState ───────────────────────────────────────
  useEffect(() => {
    setIsProcessing(systemState === 'thinking' || systemState === 'acting');
  }, [systemState]);

  // ── WebSocket message handler ─────────────────────────────────────────────────
  useEffect(() => {
    if (!lastMessage) return;
    const msg = lastMessage;

    switch (msg.type) {
      // ── Action pipeline ──────────────────────────────────────────────────────
      case 'action':
        setActions(prev => [...prev, {
          id: Date.now().toString(),
          message: msg.message || 'İşlem gerçekleştirildi',
          type: msg.source === 'autonomous' ? 'autonomous' : 'system',
          timestamp: new Date().toLocaleTimeString(),
        }]);
        break;

      // ── Streaming chat ───────────────────────────────────────────────────────
      case 'chat_chunk':
        setChatBuffer(prev => prev + (msg.text || '') + ' ');
        break;

      case 'chat_complete':
        if (chatBuffer.trim()) {
          setActions(prev => [...prev, {
            id: Date.now().toString(),
            message: `💬 ${chatBuffer.trim()}`,
            type: 'chat',
            timestamp: new Date().toLocaleTimeString(),
          }]);
        }
        setChatBuffer('');
        break;

      // ── Memory / reflection ──────────────────────────────────────────────────
      case 'memory':
      case 'reflection':
        setMemories(prev => [{
          id: Date.now().toString(),
          type: msg.type as any,
          title: msg.title || 'Hafıza Güncellendi',
          content: msg.content || msg.message || '',
          priority: msg.priority || 'medium',
          timestamp: msg.timestamp || 'Şimdi',
        }, ...prev.slice(0, 9)]);
        break;

      case 'goal':
        setMemories(prev => [{
          id: Date.now().toString(),
          type: 'goal',
          title: msg.title || 'Otonom Hedef',
          content: msg.description || msg.message || '',
          priority: msg.priority || 'medium',
          timestamp: 'Şimdi',
        }, ...prev.slice(0, 9)]);
        break;

      // ── Metrics ──────────────────────────────────────────────────────────────
      case 'metrics':
      case 'system_status':
        setMetrics(prev => prev.map(m => {
          if (m.label === 'CPU'  && msg.cpu  !== undefined) return { ...m, value: Math.round(msg.cpu) };
          if (m.label === 'RAM'  && msg.ram  !== undefined) return { ...m, value: Math.round(msg.ram) };
          if (m.label === 'DISK' && msg.disk !== undefined) return { ...m, value: Math.round(msg.disk) };
          return m;
        }));
        break;

      // ── Error ────────────────────────────────────────────────────────────────
      case 'error':
        setActions(prev => [...prev, {
          id: Date.now().toString(),
          message: `❌ ${msg.error || 'Bilinmeyen hata'}`,
          type: 'system',
          timestamp: new Date().toLocaleTimeString(),
        }]);
        break;

      // ── Approval request ─────────────────────────────────────────────────────
      case 'approval_request':
        setActions(prev => [...prev, {
          id: Date.now().toString(),
          message: `⚠️ Onay Gerekli: ${msg.command || 'Yüksek riskli işlem'}`,
          type: 'system',
          timestamp: new Date().toLocaleTimeString(),
        }]);
        setMemories(prev => [{
          id: Date.now().toString(),
          type: 'goal',
          title: '⚠️ Onay Gerekli',
          content: `İşlem: ${msg.action?.action || 'Bilinmiyor'}\nRisk: ${msg.action?.risk_level || 'yüksek'}`,
          priority: 'critical',
          timestamp: 'Şimdi',
        }, ...prev.slice(0, 9)]);
        break;

      case 'connection':
        setActions(prev => [...prev, {
          id: Date.now().toString(),
          message: `Bağlantı ${msg.status}: ${msg.system_status?.daemon_status || 'Hazır'}`,
          type: 'system',
          timestamp: new Date().toLocaleTimeString(),
        }]);
        break;

      default:
        break;
    }
  }, [lastMessage]);

  // Keep last 20 actions
  useEffect(() => {
    if (actions.length > 20) setActions(prev => prev.slice(-20));
  }, [actions]);

  // ── Submit handler ────────────────────────────────────────────────────────────
  const handleSubmit = useCallback((cmd: string) => {
    setActions(prev => [...prev, {
      id: Date.now().toString(),
      message: cmd,
      type: 'user',
      timestamp: new Date().toLocaleTimeString(),
    }]);
    sendMessage({ type: 'user_command', message: cmd, timestamp: new Date().toISOString() });
  }, [sendMessage]);

  // ── Derived ring color ────────────────────────────────────────────────────────
  const stateColor = STATE_COLORS[systemState] ?? STATE_COLORS.idle;

  return (
    <div className="relative w-full h-screen bg-black overflow-hidden">
      <TopHUD ttsEnabled={true} ttsSupported={true} onTTSToggle={() => {}} />
      <SpeechVisualizer isSpeaking={isSpeaking} />
      <div className="absolute inset-0 grid-bg opacity-40" />
      <div className="scan-line" />

      <div className="relative w-full h-full flex flex-col p-8 pt-24">

        {/* ── Top Bar ─────────────────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-12"
        >
          {/* Logo + state label */}
          <div className="flex items-center gap-4">
            <div className="relative w-12 h-12">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: systemState === 'thinking' ? 3 : 8, repeat: Infinity, ease: 'linear' }}
                className="absolute inset-0"
              >
                <svg viewBox="0 0 100 100" className="w-full h-full">
                  <circle cx="50" cy="50" r="45" stroke={stateColor.ring} strokeWidth="1.5" fill="none" />
                  <circle cx="50" cy="50" r="35" stroke={stateColor.ring} strokeWidth="1" fill="none" />
                </svg>
              </motion.div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div
                  className="w-4 h-4 rounded-full transition-all duration-500"
                  style={{ background: stateColor.ring, boxShadow: `0 0 20px ${stateColor.glow}` }}
                />
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-light tracking-[0.3em]" style={{ color: stateColor.ring, textShadow: `0 0 20px ${stateColor.glow}` }}>
                JARVIS
              </h1>
              <p className="text-[10px] tracking-[0.2em] mt-1" style={{ color: stateColor.ring, opacity: 0.7 }}>
                {isConnected ? stateColor.label : 'BAĞLANIYOR...'}
              </p>
            </div>
          </div>

          {/* Metrics */}
          <div className="flex gap-8">
            {metrics.map((metric, idx) => (
              <motion.div
                key={metric.label}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.1 }}
                className="text-center"
              >
                <div className="relative w-20 h-20 mb-2">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="40" cy="40" r="35" stroke="rgba(0,212,255,0.1)" strokeWidth="2" fill="none" />
                    <circle
                      cx="40" cy="40" r="35"
                      stroke={stateColor.ring}
                      strokeWidth="2" fill="none"
                      strokeDasharray={`${2 * Math.PI * 35}`}
                      strokeDashoffset={`${2 * Math.PI * 35 * (1 - metric.value / 100)}`}
                      style={{ transition: 'stroke-dashoffset 0.5s ease, stroke 0.5s ease', filter: `drop-shadow(0 0 5px ${stateColor.glow})` }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-sm font-light" style={{ color: stateColor.ring }}>
                      {metric.value}<span className="text-[10px]">{metric.unit}</span>
                    </span>
                  </div>
                </div>
                <span className="text-[10px] tracking-wider" style={{ color: stateColor.ring, opacity: 0.6 }}>{metric.label}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* ── Main Content ─────────────────────────────────────────────────────── */}
        <div className="flex-1 flex gap-6 min-h-0">

          {/* Left — Activity Log */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="w-80 glass-panel p-6 relative flex flex-col"
          >
            <div className="corner-accent tl" /><div className="corner-accent bl" />
            <div className="flex items-center gap-2 mb-4">
              <div className="status-indicator" />
              <h3 className="text-blue-400 text-xs tracking-[0.2em] font-light">AKTİVİTE LOGU</h3>
            </div>
            <div className="flex-1 space-y-3 custom-scrollbar overflow-y-auto">
              <AnimatePresence initial={false}>
                {actions.map((action) => (
                  <motion.div
                    key={action.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, height: 0 }}
                    className="border-l border-blue-400/30 pl-3 py-1"
                  >
                    <div className="flex items-start gap-2">
                      <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${
                        action.type === 'user'       ? 'bg-cyan-400' :
                        action.type === 'autonomous' ? 'bg-orange-400' :
                        action.type === 'chat'       ? 'bg-green-400' :
                        'bg-blue-400/50'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <p className={`text-xs font-light leading-relaxed break-words ${
                          action.type === 'user'       ? 'text-cyan-400' :
                          action.type === 'autonomous' ? 'text-orange-400' :
                          action.type === 'chat'       ? 'text-green-300' :
                          'text-blue-400/80'
                        }`}>
                          {action.message}
                        </p>
                        <span className="text-blue-400/30 text-[10px]">{action.timestamp}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={actionsEndRef} />
            </div>
          </motion.div>

          {/* Center — Holographic Rings */}
          <div className="flex-1 flex items-center justify-center relative">
            {/* Streaming chat bubble */}
            <AnimatePresence>
              {chatBuffer && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute top-4 left-1/2 -translate-x-1/2 max-w-sm bg-black/80 backdrop-blur border border-green-400/30 rounded-2xl px-5 py-3 z-10"
                >
                  <p className="text-green-300 text-sm leading-relaxed">{chatBuffer}</p>
                </motion.div>
              )}
            </AnimatePresence>

            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="relative w-96 h-96"
            >
              {/* Outer ring */}
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: systemState === 'thinking' ? 5 : 30, repeat: Infinity, ease: 'linear' }}
                className="absolute inset-0"
              >
                <svg viewBox="0 0 400 400" className="w-full h-full">
                  <circle cx="200" cy="200" r="180" stroke={stateColor.ring} strokeWidth="1" fill="none" strokeDasharray="10,10"
                    style={{ transition: 'stroke 0.5s ease' }} />
                </svg>
              </motion.div>

              {/* Middle ring */}
              <motion.div
                animate={{ rotate: -360 }}
                transition={{ duration: systemState === 'thinking' ? 3 : 20, repeat: Infinity, ease: 'linear' }}
                className="absolute inset-12"
              >
                <svg viewBox="0 0 400 400" className="w-full h-full">
                  <circle cx="200" cy="200" r="150" stroke={stateColor.ring} strokeWidth="1" fill="none" strokeDasharray="5,15"
                    style={{ transition: 'stroke 0.5s ease' }} />
                </svg>
              </motion.div>

              {/* Inner ring */}
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
                className="absolute inset-24"
              >
                <svg viewBox="0 0 400 400" className="w-full h-full">
                  <circle cx="200" cy="200" r="120" stroke={stateColor.ring} strokeWidth="1" fill="none"
                    style={{ transition: 'stroke 0.5s ease' }} />
                </svg>
              </motion.div>

              {/* Core */}
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  animate={{
                    scale: isProcessing ? [1, 1.2, 1] : isSpeaking ? [1, 1.15, 1] : [1, 1.05, 1],
                    opacity: isProcessing ? [0.8, 1, 0.8] : [0.5, 0.9, 0.5],
                  }}
                  transition={{ duration: isProcessing ? 0.8 : 2.5, repeat: Infinity }}
                  className="w-32 h-32 rounded-full"
                  style={{
                    background: `radial-gradient(circle, ${stateColor.ring}33, transparent)`,
                    boxShadow: `0 0 80px ${stateColor.glow}, inset 0 0 40px ${stateColor.glow}`,
                    transition: 'box-shadow 0.5s ease',
                  }}
                />
              </div>

              {/* Orbiting dots */}
              {[0, 120, 240].map((angle, idx) => (
                <motion.div
                  key={idx}
                  animate={{ rotate: 360 }}
                  transition={{ duration: 10 + idx * 2, repeat: Infinity, ease: 'linear' }}
                  className="absolute inset-0"
                >
                  <div
                    className="absolute w-2 h-2 rounded-full"
                    style={{
                      top: '50%', left: '50%',
                      transform: `rotate(${angle}deg) translateX(140px)`,
                      background: stateColor.ring,
                      boxShadow: `0 0 10px ${stateColor.glow}`,
                      transition: 'background 0.5s ease',
                    }}
                  />
                </motion.div>
              ))}
            </motion.div>
          </div>

          {/* Right — Memory & Goals */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="w-80 glass-panel p-6 relative flex flex-col"
          >
            <div className="corner-accent tr" /><div className="corner-accent br" />
            <div className="flex items-center gap-2 mb-4">
              <div className="status-indicator" />
              <h3 className="text-blue-400 text-xs tracking-[0.2em] font-light">HAFIZA & HEDEFLER</h3>
            </div>
            <div className="flex-1 space-y-4 custom-scrollbar overflow-y-auto">
              <AnimatePresence initial={false}>
                {memories.length === 0 ? (
                  <div className="text-blue-400/40 text-xs text-center py-8">Henüz hafıza yok</div>
                ) : (
                  memories.map((memory, idx) => (
                    <motion.div
                      key={memory.id}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ delay: idx * 0.04 }}
                      className="border-l border-blue-400/30 pl-3 py-2"
                    >
                      <div className="flex items-start gap-2">
                        <span className={`text-sm flex-shrink-0 ${
                          memory.type === 'goal'       ? 'text-orange-400' :
                          memory.type === 'reflection' ? 'text-blue-400' :
                          'text-purple-400'
                        }`}>
                          {memory.type === 'goal' ? '🎯' : memory.type === 'reflection' ? '💭' : '🧠'}
                        </span>
                        <div className="flex-1 min-w-0">
                          <p className="text-blue-400 text-xs font-light mb-1 truncate">{memory.title}</p>
                          <p className="text-blue-400/60 text-[10px] leading-relaxed line-clamp-3">{memory.content}</p>
                          <span className="text-blue-400/30 text-[9px]">{memory.timestamp}</span>
                        </div>
                      </div>
                    </motion.div>
                  ))
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>

        {/* ── Command Input ─────────────────────────────────────────────────────── */}
        <CommandInput
          onSubmit={handleSubmit}
          isProcessing={isProcessing}
          isSpeaking={isSpeaking}
          onInterrupt={interruptSpeech}
          systemState={systemState}
        />
      </div>
    </div>
  );
}

export default App;
