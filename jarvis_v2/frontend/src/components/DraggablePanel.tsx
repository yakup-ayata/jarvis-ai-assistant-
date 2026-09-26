import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface DraggablePanelProps {
  children: ReactNode;
  className?: string;
  dragConstraints?: {
    top?: number;
    left?: number;
    right?: number;
    bottom?: number;
  };
}

export const DraggablePanel: React.FC<DraggablePanelProps> = ({
  children,
  className = '',
  dragConstraints = { top: 0, left: 0, right: 500, bottom: 500 }
}) => {
  return (
    <motion.div
      drag
      dragConstraints={dragConstraints}
      dragElastic={0.1}
      dragTransition={{ bounceStiffness: 300, bounceDamping: 20 }}
      whileDrag={{ scale: 1.05, cursor: 'grabbing' }}
      className={`cursor-grab active:cursor-grabbing ${className}`}
    >
      {children}
    </motion.div>
  );
};
