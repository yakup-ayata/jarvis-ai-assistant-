import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Action {
  id: string;
  message: string;
  type: 'user' | 'autonomous';
  timestamp: string;
}

interface ActionLogPanelProps {
  actions: Action[];
}

export const ActionLogPanel: React.FC<ActionLogPanelProps> = ({ actions }) => {
  return (
    <motion.div
      initial={{ x: -300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="fixed left-4 top-20 bottom-24 w-80 bg-black bg-opacity-50 backdrop-blur-md rounded-lg border border-cyan-500/30 shadow-[0_0_30px_rgba(0,255,255,0.2)] overflow-hidden flex flex-col"
    >
      {/* Header */}
      <div className="p-4 border-b border-cyan-500/30 bg-gradient-to-r from-cyan-900/20 to-blue-900/20">
        <h2 className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
          Action Log
        </h2>
        <p className="text-xs text-gray-400 mt-1">{actions.length} actions recorded</p>
      </div>

      {/* Actions List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2 custom-scrollbar">
        <AnimatePresence>
          {actions.map((action, idx) => (
            <motion.div
              key={action.id}
              initial={{ opacity: 0, x: -20, scale: 0.9 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 20, scale: 0.9 }}
              transition={{ duration: 0.3, delay: idx * 0.05 }}
              whileHover={{
                scale: 1.02,
                boxShadow: action.type === 'user'
                  ? '0 0 20px rgba(255, 165, 0, 0.5)'
                  : '0 0 20px rgba(0, 255, 255, 0.5)'
              }}
              className={`p-3 rounded-lg border cursor-pointer transition-all ${
                action.type === 'user'
                  ? 'bg-gradient-to-r from-orange-600/20 to-orange-700/20 border-orange-500/30 hover:border-orange-400'
                  : 'bg-gradient-to-r from-cyan-600/20 to-blue-700/20 border-cyan-500/30 hover:border-cyan-400'
              }`}
            >
              <div className="flex items-start gap-2">
                <motion.div
                  animate={{
                    rotate: [0, 360],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'linear'
                  }}
                  className={`w-2 h-2 rounded-full mt-1 ${
                    action.type === 'user' ? 'bg-orange-400' : 'bg-cyan-400'
                  }`}
                />
                <div className="flex-1">
                  <p className="text-sm text-white leading-relaxed">{action.message}</p>
                  <p className="text-xs text-gray-400 mt-1">{action.timestamp}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {actions.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center text-gray-500 py-8"
          >
            <p className="text-sm">No actions yet</p>
            <p className="text-xs mt-2">Actions will appear here as they occur</p>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};
