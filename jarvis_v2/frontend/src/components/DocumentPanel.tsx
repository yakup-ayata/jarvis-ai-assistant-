import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Document {
  source: string;
  chunks: number;
}

interface DocumentPanelProps {
  documents: Document[];
  onDelete: (source: string) => void;
  onRefresh: () => void;
}

export const DocumentPanel: React.FC<DocumentPanelProps> = ({ 
  documents, 
  onDelete, 
  onRefresh 
}) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="document-panel"
    >
      <div className="panel-header">
        <h3>Documents ({documents.length})</h3>
        <button onClick={onRefresh} className="refresh-button" title="Refresh">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="23 4 23 10 17 10" />
            <polyline points="1 20 1 14 7 14" />
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
          </svg>
        </button>
      </div>

      <div className="documents-list">
        <AnimatePresence>
          {documents.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="empty-state"
            >
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              <p>No documents uploaded</p>
            </motion.div>
          ) : (
            documents.map((doc, index) => (
              <motion.div
                key={doc.source}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.05 }}
                className="document-item"
              >
                <div className="document-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                    <polyline points="10 9 9 9 8 9" />
                  </svg>
                </div>
                
                <div className="document-info">
                  <div className="document-name">{doc.source}</div>
                  <div className="document-meta">{doc.chunks} chunks</div>
                </div>

                <button
                  onClick={() => onDelete(doc.source)}
                  className="delete-button"
                  title="Delete document"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                  </svg>
                </button>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      <style>{`
        .document-panel {
          background: rgba(0, 20, 40, 0.6);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(0, 183, 255, 0.2);
          border-radius: 8px;
          padding: 1rem;
          max-height: 400px;
          display: flex;
          flex-direction: column;
        }

        .panel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          padding-bottom: 0.75rem;
          border-bottom: 1px solid rgba(0, 183, 255, 0.2);
        }

        .panel-header h3 {
          margin: 0;
          font-size: 1rem;
          font-weight: 600;
          color: rgba(0, 183, 255, 0.9);
          font-family: 'Orbitron', monospace;
        }

        .refresh-button {
          background: transparent;
          border: 1px solid rgba(0, 183, 255, 0.3);
          border-radius: 4px;
          padding: 0.5rem;
          color: rgba(0, 183, 255, 0.7);
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .refresh-button:hover {
          background: rgba(0, 183, 255, 0.1);
          border-color: rgba(0, 183, 255, 0.5);
          color: rgba(0, 183, 255, 1);
        }

        .documents-list {
          flex: 1;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .documents-list::-webkit-scrollbar {
          width: 6px;
        }

        .documents-list::-webkit-scrollbar-track {
          background: rgba(0, 183, 255, 0.05);
          border-radius: 3px;
        }

        .documents-list::-webkit-scrollbar-thumb {
          background: rgba(0, 183, 255, 0.3);
          border-radius: 3px;
        }

        .documents-list::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 183, 255, 0.5);
        }

        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 2rem;
          color: rgba(255, 255, 255, 0.4);
          text-align: center;
        }

        .empty-state svg {
          margin-bottom: 1rem;
          opacity: 0.5;
        }

        .empty-state p {
          margin: 0;
          font-size: 0.875rem;
        }

        .document-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem;
          background: rgba(0, 183, 255, 0.05);
          border: 1px solid rgba(0, 183, 255, 0.15);
          border-radius: 6px;
          transition: all 0.3s ease;
        }

        .document-item:hover {
          background: rgba(0, 183, 255, 0.1);
          border-color: rgba(0, 183, 255, 0.3);
          transform: translateX(4px);
        }

        .document-icon {
          color: rgba(0, 183, 255, 0.6);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .document-info {
          flex: 1;
          min-width: 0;
        }

        .document-name {
          font-size: 0.875rem;
          color: rgba(255, 255, 255, 0.9);
          font-family: 'Orbitron', monospace;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .document-meta {
          font-size: 0.75rem;
          color: rgba(255, 255, 255, 0.5);
          margin-top: 0.25rem;
        }

        .delete-button {
          background: transparent;
          border: 1px solid rgba(255, 50, 50, 0.3);
          border-radius: 4px;
          padding: 0.5rem;
          color: rgba(255, 50, 50, 0.7);
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .delete-button:hover {
          background: rgba(255, 50, 50, 0.1);
          border-color: rgba(255, 50, 50, 0.5);
          color: rgba(255, 50, 50, 1);
        }
      `}</style>
    </motion.div>
  );
};
