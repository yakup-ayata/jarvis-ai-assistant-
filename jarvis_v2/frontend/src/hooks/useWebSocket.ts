/**
 * WebSocket Hook
 * Backend ile gerçek zamanlı iletişim için custom hook
 * Message queue + retry + interrupt mekanizması
 */

import { useEffect, useRef, useState, useCallback } from 'react';

export type SystemState = 'idle' | 'listening' | 'thinking' | 'acting';

interface UseWebSocketReturn {
  isConnected: boolean;
  messages: any[];
  sendMessage: (message: any) => void;
  lastMessage: any;
  systemState: SystemState;
  interruptSpeech: () => void;   // JARVIS konuşurken kes
  isSpeaking: boolean;           // TTS aktif mi?
}

interface QueuedMessage {
  message: any;
  timestamp: number;
  retries: number;
}

export function useWebSocket(url: string): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [systemState, setSystemState] = useState<SystemState>('idle');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number>();
  const reconnectAttemptsRef = useRef(0);
  const isConnectingRef = useRef(false);
  const messageQueueRef = useRef<QueuedMessage[]>([]);
  // Streaming chat buffer — cümleleri birleştirmek için
  const chatBufferRef = useRef<string>('');
  const MAX_RECONNECT_ATTEMPTS = 5;
  const MAX_QUEUE_SIZE = 100;
  const MAX_RETRIES = 3;

  const processQueue = useCallback(() => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    const queue = messageQueueRef.current;
    const failedMessages: QueuedMessage[] = [];

    while (queue.length > 0) {
      const item = queue.shift();
      if (!item) continue;

      try {
        wsRef.current.send(JSON.stringify(item.message));
        console.log('📤 Sent queued message:', item.message);
      } catch (error) {
        console.error('❌ Error sending queued message:', error);
        
        // Retry logic
        if (item.retries < MAX_RETRIES) {
          failedMessages.push({
            ...item,
            retries: item.retries + 1
          });
        } else {
          console.error('❌ Message dropped after max retries:', item.message);
        }
      }
    }

    // Re-queue failed messages
    messageQueueRef.current = failedMessages;
  }, []);

  const connect = useCallback(() => {
    // Prevent multiple simultaneous connection attempts
    if (isConnectingRef.current || wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('⏭️  Connection already in progress or established');
      return;
    }

    // Check max attempts
    if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
      console.error('❌ Max reconnection attempts reached. Please refresh the page.');
      return;
    }

    isConnectingRef.current = true;

    try {
      console.log(`🔌 Connecting to WebSocket: ${url} (attempt ${reconnectAttemptsRef.current + 1}/${MAX_RECONNECT_ATTEMPTS})`);
      
      // Close existing connection if any
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connected successfully');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        isConnectingRef.current = false;
        
        // Process queued messages
        processQueue();
        
        // Reset state on reconnect
        setSystemState('idle');
        setIsSpeaking(false);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 WebSocket message:', data);
          setMessages(prev => [...prev, data]);
          setLastMessage(data);

          // Handle System State Sync
          if (data.type === 'system_state' && data.state) {
            setSystemState(data.state as SystemState);
          }

          // TTS durum takibi
          if (data.type === 'tts_status') {
            setIsSpeaking(data.status === 'speaking');
          }

          // Streaming chat chunk'ları birleştir
          if (data.type === 'chat_chunk') {
            chatBufferRef.current += (data.text || '') + ' ';
            setIsSpeaking(true);
          }
          if (data.type === 'chat_complete') {
            chatBufferRef.current = '';
            setIsSpeaking(false);
          }
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log(`❌ WebSocket disconnected (code: ${event.code}, reason: ${event.reason})`);
        setIsConnected(false);
        isConnectingRef.current = false;
        
        // Only reconnect if not a normal closure and under max attempts
        if (event.code !== 1000 && reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          // Exponential Backoff: 1s, 2s, 4s, 8s, 16s... max 30s
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          console.log(`🔄 Reconnecting in ${delay/1000}s... (Attempt: ${reconnectAttemptsRef.current + 1}/${MAX_RECONNECT_ATTEMPTS})`);
          
          reconnectTimeoutRef.current = window.setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, delay);
        }
      };

      ws.onerror = (error) => {
        console.error('⚠️  WebSocket error:', error);
        isConnectingRef.current = false;
      };
    } catch (error) {
      console.error('❌ Error creating WebSocket:', error);
      setIsConnected(false);
      isConnectingRef.current = false;
    }
  }, [url, processQueue]);

  useEffect(() => {
    connect();

    return () => {
      console.log('🧹 Cleaning up WebSocket connection');
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
        wsRef.current = null;
      }
      isConnectingRef.current = false;
    };
  }, [connect]);

  const sendMessage = useCallback((message: any) => {
    const queuedMessage: QueuedMessage = {
      message,
      timestamp: Date.now(),
      retries: 0
    };

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify(message));
        console.log('📤 Sent WebSocket message:', message);
      } catch (error) {
        console.error('❌ Error sending WebSocket message:', error);
        
        // Add to queue for retry
        if (messageQueueRef.current.length < MAX_QUEUE_SIZE) {
          messageQueueRef.current.push(queuedMessage);
          console.log('📥 Message queued for retry');
        } else {
          console.error('❌ Message queue full, message dropped');
        }
      }
    } else {
      console.warn('⚠️  WebSocket not connected, queueing message');
      
      // Add to queue
      if (messageQueueRef.current.length < MAX_QUEUE_SIZE) {
        messageQueueRef.current.push(queuedMessage);
        console.log('📥 Message queued (disconnected)');
      } else {
        console.error('❌ Message queue full, message dropped');
      }
    }
  }, []);

  /**
   * interruptSpeech — JARVIS konuşurken kullanıcı yeni komut verirse çağrılır.
   * 1. Backend'e "interrupt" mesajı gönderir (TTS durdurulur).
   * 2. Yerel isSpeaking state'ini sıfırlar.
   */
  const interruptSpeech = useCallback(() => {
    if (!isSpeaking && systemState === 'idle') return;

    console.log('🛑 Interrupting JARVIS speech...');
    setIsSpeaking(false);
    chatBufferRef.current = '';

    // Backend'e interrupt sinyali gönder
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'interrupt_speech' }));
    }
  }, [isSpeaking, systemState]);

  return { isConnected, messages, sendMessage, lastMessage, systemState, interruptSpeech, isSpeaking };
}
