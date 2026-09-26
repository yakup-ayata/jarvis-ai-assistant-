import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface EngineeringModeProps {
  onModeChange?: (enabled: boolean) => void;
}

/**
 * Engineering Mode Toggle
 * 
 * When enabled, JARVIS can:
 * - Generate multi-language code
 * - Create fullstack projects
 * - Self-heal and optimize
 * - Execute autonomous development tasks
 */
export const EngineeringModeToggle: React.FC<EngineeringModeProps> = ({ onModeChange }) => {
  const [engineeringMode, setEngineeringMode] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    // Load from localStorage
    const saved = localStorage.getItem('engineeringMode');
    if (saved) {
      const enabled = JSON.parse(saved);
      setEngineeringMode(enabled);
      onModeChange?.(enabled);
    }
  }, [onModeChange]);

  const toggleMode = () => {
    const newMode = !engineeringMode;
    setEngineeringMode(newMode);
    localStorage.setItem('engineeringMode', JSON.stringify(newMode));
    onModeChange?.(newMode);
  };

  const features = [
    { icon: '🤖', name: 'Multi-Agent Coding', description: 'Planner, Architect, Coder agents' },
    { icon: '🔧', name: 'Self-Healing', description: 'Auto-fix build errors & crashes' },
    { icon: '⚡', name: 'Hot Reload', description: 'Live code updates without restart' },
    { icon: '🎯', name: 'Autonomous Goals', description: 'Self-directed optimization' },
    { icon: '📊', name: 'Real-time Streaming', description: 'Live code generation' },
    { icon: '🔄', name: 'Parallel Execution', description: 'Concurrent task processing' },
  ];

  return (
    <div className="engineering-mode-container">
      {/* Toggle Button */}
      <motion.div
        className="engineering-toggle"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <button
          onClick={toggleMode}
          className={`toggle-btn ${engineeringMode ? 'active' : ''}`}
        >
          <span className="toggle-icon">
            {engineeringMode ? '🔧' : '💻'}
          </span>
          <span className="toggle-label">
            Engineering Mode
          </span>
          <motion.div
            className="toggle-switch"
            animate={{
              x: engineeringMode ? 24 : 0,
              backgroundColor: engineeringMode ? '#00ff41' : '#666'
            }}
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          />
        </button>

        <button
          onClick={() => setShowDetails(!showDetails)}
          className="info-btn"
          title="Show details"
        >
          ℹ️
        </button>
      </motion.div>

      {/* Status Indicator */}
      <AnimatePresence>
        {engineeringMode && (
          <motion.div
            className="mode-status"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <div className="status-pulse" />
            <span>Engineering Mode Active</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Details Panel */}
      <AnimatePresence>
        {showDetails && (
          <motion.div
            className="details-panel"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div className="details-header">
              <h3>🔧 Engineering Mode Features</h3>
              <button onClick={() => setShowDetails(false)}>✕</button>
            </div>

            <div className="features-grid">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.name}
                  className="feature-card"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="feature-icon">{feature.icon}</div>
                  <div className="feature-content">
                    <h4>{feature.name}</h4>
                    <p>{feature.description}</p>
                  </div>
                  <div className={`feature-status ${engineeringMode ? 'enabled' : 'disabled'}`}>
                    {engineeringMode ? '✓' : '○'}
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="details-footer">
              <p>
                {engineeringMode
                  ? '✅ JARVIS can now autonomously develop, debug, and optimize code'
                  : '⚠️ Engineering features are disabled. Enable to unlock full development capabilities.'}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        .engineering-mode-container {
          position: relative;
          z-index: 100;
        }

        .engineering-toggle {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .toggle-btn {
          position: relative;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 10px 16px;
          background: rgba(0, 0, 0, 0.6);
          border: 1px solid rgba(0, 255, 65, 0.3);
          border-radius: 24px;
          color: #00ff41;
          font-family: 'Courier New', monospace;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.3s ease;
          backdrop-filter: blur(10px);
        }

        .toggle-btn:hover {
          border-color: rgba(0, 255, 65, 0.6);
          box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
        }

        .toggle-btn.active {
          background: rgba(0, 255, 65, 0.1);
          border-color: #00ff41;
          box-shadow: 0 0 30px rgba(0, 255, 65, 0.4);
        }

        .toggle-icon {
          font-size: 20px;
        }

        .toggle-label {
          font-weight: 600;
          letter-spacing: 0.5px;
        }

        .toggle-switch {
          position: absolute;
          right: 4px;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: #666;
        }

        .info-btn {
          width: 32px;
          height: 32px;
          background: rgba(0, 0, 0, 0.6);
          border: 1px solid rgba(0, 255, 65, 0.3);
          border-radius: 50%;
          color: #00ff41;
          font-size: 16px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .info-btn:hover {
          background: rgba(0, 255, 65, 0.1);
          border-color: #00ff41;
        }

        .mode-status {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-top: 8px;
          padding: 6px 12px;
          background: rgba(0, 255, 65, 0.1);
          border: 1px solid rgba(0, 255, 65, 0.3);
          border-radius: 12px;
          color: #00ff41;
          font-size: 12px;
          font-family: 'Courier New', monospace;
        }

        .status-pulse {
          width: 8px;
          height: 8px;
          background: #00ff41;
          border-radius: 50%;
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 1;
            transform: scale(1);
          }
          50% {
            opacity: 0.5;
            transform: scale(1.2);
          }
        }

        .details-panel {
          position: absolute;
          top: 100%;
          left: 0;
          margin-top: 12px;
          width: 600px;
          max-width: 90vw;
          background: rgba(0, 0, 0, 0.95);
          border: 1px solid rgba(0, 255, 65, 0.3);
          border-radius: 12px;
          overflow: hidden;
          backdrop-filter: blur(20px);
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8);
        }

        .details-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          background: rgba(0, 255, 65, 0.05);
          border-bottom: 1px solid rgba(0, 255, 65, 0.2);
        }

        .details-header h3 {
          margin: 0;
          color: #00ff41;
          font-size: 18px;
          font-family: 'Courier New', monospace;
        }

        .details-header button {
          background: none;
          border: none;
          color: #00ff41;
          font-size: 20px;
          cursor: pointer;
          opacity: 0.7;
          transition: opacity 0.3s;
        }

        .details-header button:hover {
          opacity: 1;
        }

        .features-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
          padding: 20px;
        }

        .feature-card {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          background: rgba(0, 255, 65, 0.03);
          border: 1px solid rgba(0, 255, 65, 0.2);
          border-radius: 8px;
          transition: all 0.3s ease;
        }

        .feature-card:hover {
          background: rgba(0, 255, 65, 0.08);
          border-color: rgba(0, 255, 65, 0.4);
          transform: translateX(4px);
        }

        .feature-icon {
          font-size: 24px;
          flex-shrink: 0;
        }

        .feature-content {
          flex: 1;
        }

        .feature-content h4 {
          margin: 0 0 4px 0;
          color: #00ff41;
          font-size: 14px;
          font-family: 'Courier New', monospace;
        }

        .feature-content p {
          margin: 0;
          color: rgba(0, 255, 65, 0.7);
          font-size: 12px;
        }

        .feature-status {
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          font-size: 14px;
          flex-shrink: 0;
        }

        .feature-status.enabled {
          background: rgba(0, 255, 65, 0.2);
          color: #00ff41;
        }

        .feature-status.disabled {
          background: rgba(255, 255, 255, 0.1);
          color: rgba(255, 255, 255, 0.3);
        }

        .details-footer {
          padding: 16px 20px;
          background: rgba(0, 255, 65, 0.05);
          border-top: 1px solid rgba(0, 255, 65, 0.2);
        }

        .details-footer p {
          margin: 0;
          color: rgba(0, 255, 65, 0.8);
          font-size: 13px;
          line-height: 1.5;
        }

        @media (max-width: 768px) {
          .features-grid {
            grid-template-columns: 1fr;
          }

          .details-panel {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default EngineeringModeToggle;
