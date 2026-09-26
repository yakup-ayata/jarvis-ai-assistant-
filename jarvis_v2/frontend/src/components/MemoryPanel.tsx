import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Memory {
  id: string;
  type: 'reflection' | 'goal';
  title: string;
  content: string;
  priority?: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
}

interface MemoryPanelProps {
  memories: Memory[];
}

export const MemoryPanel: React.FC<MemoryPanelProps> = ({ memories }) => {
  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'critical': return 'from-red-500 to-red-600';
      case 'high': return 'from-orange-500 to-orange-600';
      case 'medium': return 'from-yellow-500 to-yellow-600';
      case 'low': return 'from-blue-500 to-blue-600';
      default: return 'from-cyan-500 to-blue-600';
    }
  };

  const getPriorityIcon = (priority?: string) => {
    switch (priority) {
      case 'critical': return '🚨';
      case 'high': return '🔥';
      case 'medium': return '⚡';
      case 'low': return '💡';
      default: return '🧠';
    }
  };

  return (
    <motion.div
      initial={{ x: 300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="fixed right-4 top-20 bottom-24 w-80 bg-black bg-opacity-50 backdrop-blur-md rounded-lg border border-cyan-500/30 shadow-[0_0_30px_rgba(0,255,255,0.2)] overflow-hidden flex flex-col"
    >
      {/* Header */}
      <div className="p-4 border-b border-cyan-500/30 bg-gradient-to-r from-cyan-900/20 to-blue-900/20">
        <h2 className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
          Memory & Goals
        </h2>
        <p className="text-xs text-gray-400 mt-1">{memories.length} items in memory</p>
      </div>

      {/* Memory Cards */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
        <AnimatePresence>
          {memories.map((memory, idx) => (
            <motion.div
              key={memory.id}
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.9 }}
              transition={{
                duration: 0.4,
                delay: idx * 0.05,
                type: 'spring',
                stiffness: 200
              }}
              whileHover={{
                scale: 1.03,
                y: -5,
                boxShadow: '0 10px 30px rgba(0, 255, 255, 0.3)'
              }}
              className={`p-4 rounded-lg border border-cyan-500/30 bg-gradient-to-br ${getPriorityColor(memory.priority)}/10 cursor-pointer backdrop-blur-sm`}
            >
              {/* Card Header */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <motion.span
                    animate={{
                      scale: [1, 1.2, 1],
                      rotate: [0, 10, -10, 0]
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: 'easeInOut'
                    }}
                    className="text-2xl"
                  >
                    {getPriorityIcon(memory.priority)}
                  </motion.span>
                  <div>
                    <h3 className="text-sm font-semibold text-white">{memory.title}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full bg-gradient-to-r ${getPriorityColor(memory.priority)} text-white`}>
                      {memory.type}
                    </span>
                  </div>
                </div>
              </div>

              {/* Card Content */}
              <p className="text-sm text-gray-300 leading-relaxed mb-2">
                {memory.content}
              </p>

              {/* Card Footer */}
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>{memory.timestamp}</span>
                {memory.priority && (
                  <span className="uppercase tracking-wider">{memory.priority}</span>
                )}
              </div>

              {/* Glow Effect */}
              <motion.div
                className={`absolute inset-0 rounded-lg bg-gradient-to-r ${getPriorityColor(memory.priority)} opacity-0`}
                whileHover={{ opacity: 0.1 }}
                transition={{ duration: 0.3 }}
              />
            </motion.div>
          ))}
        </AnimatePresence>

        {memories.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center text-gray-500 py-8"
          >
            <p className="text-sm">No memories yet</p>
            <p className="text-xs mt-2">Reflections and goals will appear here</p>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};
