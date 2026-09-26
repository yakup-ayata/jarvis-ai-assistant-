import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Cpu, Wifi, HardDrive, Activity, Play, Pause, SkipBack, SkipForward } from 'lucide-react';
import axios from 'axios';
import { ExecutionStatus } from './components/ExecutionStatus';
import { WindowMonitor } from './components/WindowMonitor';
import { EventLog } from './components/EventLog';
import { useWebSocket } from './hooks/useWebSocket';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8001/ws';
const API_TIMEOUT = 30000; // 30 seconds

// Retry logic for failed requests
async function fetchWithRetry(url: string, options: any, retries = 3): Promise<any> {
  for (let i = 0; i < retries; i++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);
      
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      return response;
    } catch (error: any) {
      console.error(`Attempt ${i + 1}/${retries} failed:`, error);
      
      if (i === retries - 1) throw error;
      
      // Exponential backoff
      await new Promise(r => setTimeout(r, 1000 * Math.pow(2, i)));
    }
  }
}

interface SystemStats {
  cpu: number;
  ram: number;
  temp: number;
  network: { dl: string; ul: string };
}

interface Notification {
  id: string;
  type: string;
  message: string;
  count?: number;
}

interface MediaInfo {
  title: string;
  artist: string;
  isPlaying: boolean;
}

interface WindowInfo {
  title?: string;
  application?: string;
  pid?: number;
  bounds?: [number, number, number, number];
}

interface Event {
  id: string;
  type: string;
  data: any;
  timestamp: number;
}

function App() {
  const [isListening, setIsListening] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [lastResponse, setLastResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);  // ✅ Loading state
  const [voiceError, setVoiceError] = useState<string | null>(null);  // ✅ Error state
  
  // WebSocket connection
  const { isConnected: wsConnected, lastMessage } = useWebSocket(WS_URL);
  
  // New states for automation
  const [executionState, setExecutionState] = useState('running');
  const [isPaused, setIsPaused] = useState(false);
  const [pauseInstruction, setPauseInstruction] = useState('');
  const [pauseActionType, setPauseActionType] = useState('');
  const [activeWindow, setActiveWindow] = useState<WindowInfo>({});
  const [events, setEvents] = useState<Event[]>([]);
  
  const [systemStats, setSystemStats] = useState<SystemStats>({
    cpu: 24,
    ram: 38,
    temp: 42,
    network: { dl: '250Mbps', ul: '50Mbps' }
  });
  const [notifications] = useState<Notification[]>([
    { id: '1', type: 'email', message: 'Email notifications', count: 8 },
    { id: '2', type: 'reminder', message: 'Email reminder after meeting' },
    { id: '3', type: 'message', message: 'Messages', count: 3 }
  ]);
  const [mediaInfo, setMediaInfo] = useState<MediaInfo>({
    title: 'Across the Universe',
    artist: 'Beatles - Rock',
    isPlaying: false
  });
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const recognitionRef = useRef<any>(null);

  // WebSocket message handler
  useEffect(() => {
    if (!lastMessage) return;

    console.log('📨 Processing WebSocket message:', lastMessage);

    switch (lastMessage.type) {
      case 'execution_state':
        setExecutionState(lastMessage.state);
        setIsPaused(lastMessage.is_paused);
        console.log('🔄 Execution state updated:', lastMessage.state, 'Paused:', lastMessage.is_paused);
        break;

      case 'window_change':
        setActiveWindow(lastMessage.window);
        console.log('🪟 Window changed:', lastMessage.window);
        break;

      case 'event':
        setEvents(prev => [...prev, {
          id: Date.now().toString() + Math.random(),
          type: lastMessage.event_type,
          data: lastMessage.data,
          timestamp: lastMessage.timestamp
        }]);
        console.log('📋 Event added:', lastMessage.event_type);
        break;

      case 'pause_notification':
        setPauseInstruction(lastMessage.instruction);
        setPauseActionType(lastMessage.action);
        console.log('⏸️  Pause notification:', lastMessage.instruction);
        break;

      case 'resume_notification':
        setPauseInstruction('');
        setPauseActionType('');
        console.log('▶️  Resume notification');
        break;

      case 'connected':
        console.log('✅ WebSocket connected:', lastMessage.message);
        break;
    }
  }, [lastMessage]);

  // Audio visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 120;

    let phase = 0;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Outer glow circle
      const gradient = ctx.createRadialGradient(centerX, centerY, radius - 20, centerX, centerY, radius + 40);
      gradient.addColorStop(0, 'rgba(0, 150, 255, 0.3)');
      gradient.addColorStop(1, 'rgba(0, 150, 255, 0)');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius + 40, 0, Math.PI * 2);
      ctx.fill();

      // Main circle
      ctx.strokeStyle = '#0096ff';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.stroke();

      // Inner circle
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius - 20, 0, Math.PI * 2);
      ctx.stroke();

      // Audio waveform
      if (isListening || isRecording) {
        ctx.strokeStyle = '#00d4ff';
        ctx.lineWidth = 2;
        ctx.beginPath();

        const bars = 60;
        for (let i = 0; i < bars; i++) {
          const angle = (i / bars) * Math.PI * 2;
          const wave = Math.sin(angle * 3 + phase) * 15 + Math.random() * 10;
          const x1 = centerX + Math.cos(angle) * (radius - 15);
          const y1 = centerY + Math.sin(angle) * (radius - 15);
          const x2 = centerX + Math.cos(angle) * (radius - 15 - wave);
          const y2 = centerY + Math.sin(angle) * (radius - 15 - wave);

          ctx.moveTo(x1, y1);
          ctx.lineTo(x2, y2);
        }
        ctx.stroke();

        phase += 0.1;
      } else {
        // Idle pulse
        const pulseRadius = radius - 15 + Math.sin(phase) * 5;
        ctx.strokeStyle = '#0096ff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(centerX, centerY, pulseRadius, 0, Math.PI * 2);
        ctx.stroke();

        phase += 0.05;
      }

      // Center dot
      ctx.fillStyle = (isListening || isRecording) ? '#00ff88' : '#0096ff';
      ctx.beginPath();
      ctx.arc(centerX, centerY, 8, 0, Math.PI * 2);
      ctx.fill();

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isListening, isRecording]);

  // Simulate system stats updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemStats({
        cpu: Math.floor(Math.random() * 30) + 20,
        ram: Math.floor(Math.random() * 20) + 30,
        temp: Math.floor(Math.random() * 10) + 38,
        network: { dl: '250Mbps', ul: '50Mbps' }
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // Initialize Web Speech API and load voices
  useEffect(() => {
    console.log('🎤 Initializing Speech Recognition...');
    
    // Load conversation history from localStorage
    const savedTranscript = localStorage.getItem('jarvis_last_transcript');
    const savedResponse = localStorage.getItem('jarvis_last_response');
    if (savedTranscript) setCurrentTranscript(savedTranscript);
    if (savedResponse) setLastResponse(savedResponse);
    
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = true; // Show interim results
      recognition.lang = 'tr-TR'; // Turkish
      recognition.maxAlternatives = 1;
      
      recognition.onstart = () => {
        console.log('✅ Speech recognition started');
        setIsRecording(true);
        setIsListening(true);
        setCurrentTranscript('Dinliyorum...');
      };
      
      recognition.onresult = async (event: any) => {
        console.log('📝 Speech recognition result:', event);
        
        // Get the transcript
        const result = event.results[event.results.length - 1];
        const transcript = result[0].transcript;
        const isFinal = result.isFinal;
        
        console.log(`Transcript (${isFinal ? 'final' : 'interim'}):`, transcript);
        
        if (isFinal) {
          setCurrentTranscript(transcript);
          setIsListening(true);
          setIsRecording(false);
          
          // Send to backend API
          try {
            await sendCommandToAPI(transcript);
          } catch (error) {
            console.error('❌ Error sending command:', error);
            setLastResponse('Komut gönderilemedi: ' + error);
          }
        } else {
          // Show interim results
          setCurrentTranscript(transcript + '...');
        }
      };
      
      recognition.onerror = (event: any) => {
        console.error('❌ Speech recognition error:', event.error, event);
        setIsListening(false);
        setIsRecording(false);
        
        let errorMsg = 'Ses tanıma hatası: ';
        switch (event.error) {
          case 'no-speech':
            errorMsg += 'Ses algılanamadı. Lütfen tekrar deneyin.';
            break;
          case 'audio-capture':
            errorMsg += 'Mikrofon erişimi yok. Lütfen izin verin.';
            break;
          case 'not-allowed':
            errorMsg += 'Mikrofon izni reddedildi.';
            break;
          case 'network':
            errorMsg += 'Ağ hatası. İnternet bağlantınızı kontrol edin.';
            break;
          default:
            errorMsg += event.error;
        }
        
        setVoiceError(errorMsg);  // ✅ Show error
        setLastResponse(errorMsg);
        
        // Auto-clear error after 5 seconds
        setTimeout(() => setVoiceError(null), 5000);
      };
      
      recognition.onend = () => {
        console.log('🛑 Speech recognition ended');
        setIsListening(false);
        setIsRecording(false);
      };
      
      recognitionRef.current = recognition;
      console.log('✅ Speech recognition initialized');
    } else {
      console.error('❌ Speech recognition not supported');
      alert('Tarayıcınız ses tanımayı desteklemiyor. Chrome veya Edge kullanın.');
    }

    // Load voices for TTS
    const loadVoices = () => {
      const voices = window.speechSynthesis.getVoices();
      console.log('🔊 Available voices:', voices.length);
      voices.forEach(v => console.log(`  - ${v.name} (${v.lang})`));
    };

    // Load voices on mount and when they change
    if (window.speechSynthesis) {
      loadVoices();
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }
  }, []);

  // Send command to JARVIS API
  const sendCommandToAPI = async (command: string): Promise<any> => {
    if (isLoading) {
      console.log('⚠️  Already processing a command, please wait');
      return { success: false, error: 'Already processing' };
    }
    
    console.log('📤 Sending command to API:', command);
    
    try {
      setIsLoading(true);  // ✅ Set loading
      setLastResponse('İşleniyor...');
      
      const response = await axios.post(`${API_URL}/api/v1/chat`, {
        message: command,
        stream: false
      }, {
        timeout: API_TIMEOUT,
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('📥 API Response:', response.data);
      
      const jarvisResponse = response.data.response;
      setLastResponse(jarvisResponse);
      
      // Save to localStorage
      localStorage.setItem('jarvis_last_transcript', command);
      localStorage.setItem('jarvis_last_response', jarvisResponse);
      
      // Speak response with Daniel voice
      speakText(jarvisResponse);
      
      return response.data;
      
    } catch (error: any) {
      console.error('❌ API error:', error);
      
      let errorMsg = 'Hata: ';
      if (error.code === 'ECONNABORTED') {
        errorMsg += 'İstek zaman aşımına uğradı';
      } else if (error.response) {
        errorMsg += error.response.data?.detail || error.response.statusText;
      } else if (error.request) {
        errorMsg += 'Backend bağlantısı kurulamadı. Backend çalışıyor mu kontrol edin.';
      } else {
        errorMsg += error.message;
      }
      
      setLastResponse(errorMsg);
      return { success: false, error: errorMsg };
    } finally {
      setIsLoading(false);  // ✅ Clear loading
    }
  };

  // Text to speech with JARVIS-like voice (Daniel preferred)
  const speakText = (text: string) => {
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Get available voices
      const voices = window.speechSynthesis.getVoices();
      
      // Priority 1: Daniel (UK English - our preferred JARVIS voice)
      // Priority 2: Other deep male voices
      const jarvisVoice = voices.find(voice => 
        voice.name.includes('Daniel')  // UK English male - BEST for JARVIS
      ) || voices.find(voice => 
        voice.name.includes('Alex')    // US English male
      ) || voices.find(voice => 
        voice.name.includes('Fred')    // US English male (robotic)
      ) || voices.find(voice => 
        voice.lang.startsWith('en') && voice.name.toLowerCase().includes('male')
      ) || voices.find(voice => voice.lang.startsWith('en'));
      
      if (jarvisVoice) {
        utterance.voice = jarvisVoice;
        console.log('🎤 Using JARVIS voice:', jarvisVoice.name);
      } else {
        console.warn('⚠️ Daniel voice not found. Install it from System Settings → Accessibility → Spoken Content → Manage Voices');
      }
      
      // JARVIS voice characteristics (optimized for Daniel)
      utterance.lang = 'en-GB';     // British English for Daniel
      utterance.rate = 0.9;         // Slightly slower for clarity
      utterance.pitch = 0.75;       // Lower pitch for deep, authoritative sound
      utterance.volume = 1.0;
      
      window.speechSynthesis.speak(utterance);
    }
  };

  // Toggle listening with Web Speech API
  const toggleListening = () => {
    console.log('🎤 Toggle listening. Current state:', { isRecording, isListening });
    
    if (isRecording) {
      // Stop recording
      console.log('🛑 Stopping recognition...');
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (error) {
          console.error('Error stopping recognition:', error);
        }
      }
      setIsRecording(false);
      setIsListening(false);
    } else {
      // Start recording
      if (!recognitionRef.current) {
        console.error('❌ Recognition not initialized');
        alert('Ses tanıma sistemi hazır değil. Sayfayı yenileyin.');
        return;
      }
      
      console.log('▶️ Starting recognition...');
      try {
        recognitionRef.current.start();
        // State will be updated in onstart callback
      } catch (error: any) {
        console.error('❌ Error starting recognition:', error);
        
        if (error.message && error.message.includes('already started')) {
          console.log('Recognition already running, stopping first...');
          recognitionRef.current.stop();
          setTimeout(() => {
            try {
              recognitionRef.current.start();
            } catch (e) {
              console.error('Failed to restart:', e);
            }
          }, 100);
        } else {
          alert('Ses tanıma başlatılamadı: ' + error.message);
        }
      }
    }
  };

  // Media controls - Spotify/Apple Music integration
  const togglePlayPause = async () => {
    console.log('🎵 Toggle play/pause');
    try {
      const command = mediaInfo.isPlaying ? 'müziği duraklat' : 'müziği çal';
      const result = await sendCommandToAPI(command);
      if (result?.success !== false) {
        setMediaInfo(prev => ({ ...prev, isPlaying: !prev.isPlaying }));
      }
    } catch (error) {
      console.error('❌ Media control error:', error);
    }
  };

  const skipPrevious = async () => {
    console.log('⏮ Skip previous');
    try {
      await sendCommandToAPI('önceki şarkı');
    } catch (error) {
      console.error('❌ Media control error:', error);
    }
  };

  const skipNext = async () => {
    console.log('⏭ Skip next');
    try {
      await sendCommandToAPI('sonraki şarkı');
    } catch (error) {
      console.error('❌ Media control error:', error);
    }
  };

  // Play specific song
  const playSpecificSong = async (songName: string) => {
    console.log('🎵 Play specific song:', songName);
    try {
      const result = await sendCommandToAPI(`${songName} çal`);
      if (result?.success !== false) {
        setMediaInfo(prev => ({ 
          ...prev, 
          isPlaying: true,
          title: songName,
          artist: 'Playing...'
        }));
      }
    } catch (error) {
      console.error('❌ Media control error:', error);
    }
  };

  // Handle notification clicks
  const handleNotificationClick = async (notif: Notification) => {
    console.log('🔔 Notification clicked:', notif);
    
    try {
      if (notif.type === 'email') {
        await sendCommandToAPI('Gmail aç');
      } else if (notif.type === 'message') {
        await sendCommandToAPI('Messages aç');
      } else if (notif.type === 'reminder') {
        await sendCommandToAPI('Calendar aç');
      }
    } catch (error) {
      console.error('❌ Notification click error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-black text-cyan-400 font-mono overflow-hidden relative">
      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-cyan-400 mx-auto mb-4"></div>
            <div className="text-cyan-400 text-sm">Processing command...</div>
          </div>
        </div>
      )}

      {/* Error Toast */}
      {voiceError && (
        <div className="fixed top-4 right-4 bg-red-500/90 backdrop-blur text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            <span className="text-sm font-semibold">{voiceError}</span>
          </div>
        </div>
      )}

      {/* Animated background grid */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: 'linear-gradient(#0096ff 1px, transparent 1px), linear-gradient(90deg, #0096ff 1px, transparent 1px)',
          backgroundSize: '50px 50px'
        }} />
      </div>

      {/* Header */}
      <div className="relative z-10 border-b border-cyan-900 bg-black/80 backdrop-blur">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="text-2xl font-bold tracking-wider">
              <span className="text-cyan-400">J.A.R.V.I.S.</span>
            </div>
            <div className="text-sm text-cyan-600">
              | SYSTEMS ONLINE | VOICE INTERFACE ACTIVE
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
              <span className="text-xs text-cyan-600">
                {wsConnected ? 'WEBSOCKET CONNECTED' : 'WEBSOCKET DISCONNECTED'}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-xs text-cyan-600">API CONNECTED</span>
            </div>
          </div>
        </div>
      </div>

      <div className="relative z-10 container mx-auto px-6 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Left Panel - System Monitor */}
          <div className="col-span-3 space-y-4">
            <div className="border border-cyan-900 bg-black/60 backdrop-blur p-4 rounded">
              <div className="text-xs text-cyan-600 mb-3 tracking-wider">SYSTEM MONITOR</div>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span>CPU</span>
                    <span>{systemStats.cpu}%</span>
                  </div>
                  <div className="h-1 bg-cyan-950 rounded overflow-hidden">
                    <div 
                      className="h-full bg-cyan-400 transition-all duration-300"
                      style={{ width: `${systemStats.cpu}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span>RAM</span>
                    <span>{systemStats.ram}%</span>
                  </div>
                  <div className="h-1 bg-cyan-950 rounded overflow-hidden">
                    <div 
                      className="h-full bg-cyan-400 transition-all duration-300"
                      style={{ width: `${systemStats.ram}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-xs mb-1">
                    <span>Temp</span>
                    <span>{systemStats.temp}°C</span>
                  </div>
                  <div className="h-1 bg-cyan-950 rounded overflow-hidden">
                    <div 
                      className="h-full bg-cyan-400 transition-all duration-300"
                      style={{ width: `${(systemStats.temp / 100) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="border border-cyan-900 bg-black/60 backdrop-blur p-4 rounded">
              <div className="text-xs text-cyan-600 mb-3 tracking-wider">NETWORK STATUS</div>
              <div className="space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-cyan-600">DL:</span>
                  <span>{systemStats.network.dl}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-cyan-600">UL:</span>
                  <span>{systemStats.network.ul}</span>
                </div>
              </div>
            </div>

            {/* Execution Status - NEW */}
            <ExecutionStatus
              state={executionState}
              isPaused={isPaused}
              instruction={pauseInstruction}
              actionType={pauseActionType}
            />

            {/* Window Monitor - NEW */}
            <WindowMonitor window={activeWindow} />

            <div className="border border-cyan-900 bg-black/60 backdrop-blur p-4 rounded">
              <div className="text-xs text-cyan-600 mb-3 tracking-wider">QUICK COMMANDS</div>
              <div className="space-y-2 text-xs">
                <button 
                  onClick={async () => {
                    console.log('🔘 Quick command: Safari aç');
                    await sendCommandToAPI('Safari aç');
                  }}
                  className="w-full text-left flex items-center space-x-2 text-cyan-500 hover:text-cyan-300 cursor-pointer hover:bg-cyan-900/20 p-2 rounded transition-colors"
                >
                  <div className="w-1 h-1 bg-cyan-400" />
                  <span>Open Safari</span>
                </button>
                <button 
                  onClick={async () => {
                    console.log('🔘 Quick command: Play music');
                    await playSpecificSong('Bohemian Rhapsody');
                  }}
                  className="w-full text-left flex items-center space-x-2 text-cyan-500 hover:text-cyan-300 cursor-pointer hover:bg-cyan-900/20 p-2 rounded transition-colors"
                >
                  <div className="w-1 h-1 bg-cyan-400" />
                  <span>Play Music</span>
                </button>
                <button 
                  onClick={async () => {
                    console.log('🔘 Quick command: Weather');
                    await sendCommandToAPI('hava durumu');
                  }}
                  className="w-full text-left flex items-center space-x-2 text-cyan-500 hover:text-cyan-300 cursor-pointer hover:bg-cyan-900/20 p-2 rounded transition-colors"
                >
                  <div className="w-1 h-1 bg-cyan-400" />
                  <span>Weather</span>
                </button>
                <button 
                  onClick={() => {
                    console.log('🔘 Test voice');
                    speakText("At your service, sir. All systems operational.");
                  }}
                  className="w-full text-left flex items-center space-x-2 text-cyan-500 hover:text-cyan-300 cursor-pointer hover:bg-cyan-900/20 p-2 rounded transition-colors"
                  title="Test Daniel voice"
                >
                  <div className="w-1 h-1 bg-cyan-400" />
                  <span>🎤 Test Voice</span>
                </button>
              </div>
            </div>
          </div>

          {/* Center - Main Visualization */}
          <div className="col-span-6 flex flex-col items-center justify-center">
            <div className="relative">
              <canvas 
                ref={canvasRef} 
                width={400} 
                height={400}
                className="drop-shadow-[0_0_30px_rgba(0,150,255,0.5)]"
              />
              
              {/* Mic button overlay */}
              <button
                onClick={toggleListening}
                className={`absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 
                  w-16 h-16 rounded-full border-2 transition-all duration-300
                  ${isRecording 
                    ? 'border-red-400 bg-red-400/20 shadow-[0_0_20px_rgba(255,0,0,0.5)] animate-pulse' 
                    : 'border-cyan-400 bg-cyan-400/10 hover:bg-cyan-400/20 hover:shadow-[0_0_20px_rgba(0,150,255,0.5)]'
                  }`}
              >
                {isRecording ? (
                  <MicOff className="w-8 h-8 mx-auto text-red-400" />
                ) : (
                  <Mic className="w-8 h-8 mx-auto text-cyan-400" />
                )}
              </button>
            </div>

            {/* Status text */}
            <div className="mt-8 text-center">
              <div className="text-sm text-cyan-600 mb-2">
                {isRecording ? 'RECORDING...' : isListening ? 'PROCESSING...' : 'VOICE INTERFACE READY'}
              </div>
              <div className="text-xs text-cyan-700">
                {isRecording ? 'Konuşun...' : 'Mikrofona tıklayın ve konuşun'}
              </div>
            </div>
          </div>

          {/* Right Panel - Communication Hub */}
          <div className="col-span-3 space-y-4">
            {/* Event Log - NEW */}
            <div className="h-96">
              <EventLog events={events} maxEvents={50} />
            </div>

            <div className="border border-cyan-900 bg-black/60 backdrop-blur p-4 rounded">
              <div className="text-xs text-cyan-600 mb-3 tracking-wider">WEATHER</div>
              <div className="space-y-2">
                <div className="text-lg">Istanbul, 19°C</div>
                <div className="text-xs text-cyan-600">Partly Cloudy - {new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}</div>
              </div>
            </div>

            <div className="border border-cyan-900 bg-black/60 backdrop-blur p-4 rounded">
              <div className="text-xs text-cyan-600 mb-3 tracking-wider">COMMUNICATION HUB</div>
              <div className="space-y-2 text-xs">
                {notifications.map(notif => (
                  <div 
                    key={notif.id} 
                    onClick={() => handleNotificationClick(notif)}
                    className="flex items-center space-x-2 hover:text-cyan-300 cursor-pointer transition-colors hover:bg-cyan-900/20 p-2 rounded"
                  >
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
                    <span className="flex-1">{notif.message}</span>
                    {notif.count && (
                      <span className="text-cyan-600 font-bold">{notif.count}</span>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="border border-cyan-900 bg-black/60 backdrop-blur p-4 rounded">
              <div className="text-xs text-cyan-600 mb-3 tracking-wider">MEDIA CONTROL</div>
              <div className="space-y-2">
                <div className="text-xs font-semibold">{mediaInfo.title}</div>
                <div className="text-xs text-cyan-600">{mediaInfo.artist}</div>
                <div className="flex items-center justify-center space-x-4 mt-3">
                  <button 
                    onClick={skipPrevious}
                    className="text-cyan-400 hover:text-cyan-300 transition-colors p-2 hover:bg-cyan-400/10 rounded"
                    title="Önceki şarkı"
                  >
                    <SkipBack className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={togglePlayPause}
                    className="text-cyan-400 hover:text-cyan-300 transition-colors p-2 hover:bg-cyan-400/10 rounded"
                    title={mediaInfo.isPlaying ? 'Duraklat' : 'Çal'}
                  >
                    {mediaInfo.isPlaying ? (
                      <Pause className="w-5 h-5" />
                    ) : (
                      <Play className="w-5 h-5" />
                    )}
                  </button>
                  <button 
                    onClick={skipNext}
                    className="text-cyan-400 hover:text-cyan-300 transition-colors p-2 hover:bg-cyan-400/10 rounded"
                    title="Sonraki şarkı"
                  >
                    <SkipForward className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom - Transcript */}
        <div className="mt-8 border border-cyan-900 bg-black/60 backdrop-blur rounded p-4">
          <div className="flex items-start space-x-3">
            <Activity className="w-5 h-5 text-cyan-400 mt-1 flex-shrink-0 animate-pulse" />
            <div className="flex-1 space-y-2">
              {currentTranscript && (
                <div className="text-sm">
                  <span className="text-cyan-600">KULLANICI:</span>{' '}
                  <span className="text-cyan-400">{currentTranscript}</span>
                </div>
              )}
              {lastResponse && (
                <div className="text-sm">
                  <span className="text-green-600">JARVIS:</span>{' '}
                  <span className="text-green-400">{lastResponse}</span>
                </div>
              )}
              {!currentTranscript && !lastResponse && (
                <div className="text-sm text-cyan-600">
                  Ses girişi bekleniyor... Mikrofona tıklayın ve "Safari aç" veya "Bohemian Rhapsody çal" deyin.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom taskbar */}
      <div className="absolute bottom-0 left-0 right-0 border-t border-cyan-900 bg-black/80 backdrop-blur">
        <div className="container mx-auto px-6 py-2 flex items-center justify-center space-x-6 text-xs text-cyan-600">
          <div className="flex items-center space-x-2 hover:text-cyan-400 cursor-pointer transition-colors">
            <Cpu className="w-4 h-4" />
            <span>AI Core</span>
          </div>
          <div className="flex items-center space-x-2 hover:text-cyan-400 cursor-pointer transition-colors">
            <Wifi className="w-4 h-4" />
            <span>Network</span>
          </div>
          <div className="flex items-center space-x-2 hover:text-cyan-400 cursor-pointer transition-colors">
            <HardDrive className="w-4 h-4" />
            <span>Storage</span>
          </div>
          <div className="flex items-center space-x-2 hover:text-cyan-400 cursor-pointer transition-colors">
            <Activity className="w-4 h-4" />
            <span>Analytics</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
