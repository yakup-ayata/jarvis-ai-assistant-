import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface DocumentUploadProps {
  onUpload: (filePath: string) => void;
  isProcessing: boolean;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUpload, isProcessing }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [filePath, setFilePath] = useState('');

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      // In a real implementation, you'd upload the file to a server
      // For now, we'll just use the file path
      setFilePath(file.name);
    }
  }, []);

  const handleSubmit = () => {
    if (filePath && !isProcessing) {
      onUpload(filePath);
      setFilePath('');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="document-upload"
    >
      <div
        className={`upload-zone ${isDragging ? 'dragging' : ''} ${isProcessing ? 'processing' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <AnimatePresence mode="wait">
          {isProcessing ? (
            <motion.div
              key="processing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="upload-status"
            >
              <div className="spinner" />
              <p>Processing document...</p>
            </motion.div>
          ) : (
            <motion.div
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="upload-prompt"
            >
              <svg
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              <p>Drag & drop document here</p>
              <p className="upload-hint">Supports PDF, DOCX, TXT, MD</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="upload-input-group">
        <input
          type="text"
          value={filePath}
          onChange={(e) => setFilePath(e.target.value)}
          placeholder="Or enter file path..."
          disabled={isProcessing}
          className="upload-input"
        />
        <button
          onClick={handleSubmit}
          disabled={!filePath || isProcessing}
          className="upload-button"
        >
          Upload
        </button>
      </div>

      <style>{`
        .document-upload {
          padding: 1rem;
        }

        .upload-zone {
          border: 2px dashed rgba(0, 183, 255, 0.3);
          border-radius: 8px;
          padding: 2rem;
          text-align: center;
          transition: all 0.3s ease;
          background: rgba(0, 183, 255, 0.02);
          min-height: 200px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .upload-zone.dragging {
          border-color: rgba(0, 183, 255, 0.8);
          background: rgba(0, 183, 255, 0.1);
          transform: scale(1.02);
        }

        .upload-zone.processing {
          border-color: rgba(0, 183, 255, 0.5);
          background: rgba(0, 183, 255, 0.05);
        }

        .upload-prompt svg {
          color: rgba(0, 183, 255, 0.6);
          margin-bottom: 1rem;
        }

        .upload-prompt p {
          margin: 0.5rem 0;
          color: rgba(255, 255, 255, 0.8);
        }

        .upload-hint {
          font-size: 0.875rem;
          color: rgba(255, 255, 255, 0.5);
        }

        .upload-status {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 3px solid rgba(0, 183, 255, 0.2);
          border-top-color: rgba(0, 183, 255, 0.8);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .upload-input-group {
          display: flex;
          gap: 0.5rem;
          margin-top: 1rem;
        }

        .upload-input {
          flex: 1;
          padding: 0.75rem;
          background: rgba(0, 183, 255, 0.05);
          border: 1px solid rgba(0, 183, 255, 0.2);
          border-radius: 4px;
          color: white;
          font-family: 'Orbitron', monospace;
          font-size: 0.875rem;
        }

        .upload-input:focus {
          outline: none;
          border-color: rgba(0, 183, 255, 0.5);
          background: rgba(0, 183, 255, 0.08);
        }

        .upload-input:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .upload-button {
          padding: 0.75rem 1.5rem;
          background: rgba(0, 183, 255, 0.2);
          border: 1px solid rgba(0, 183, 255, 0.4);
          border-radius: 4px;
          color: white;
          font-family: 'Orbitron', monospace;
          font-size: 0.875rem;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .upload-button:hover:not(:disabled) {
          background: rgba(0, 183, 255, 0.3);
          border-color: rgba(0, 183, 255, 0.6);
          box-shadow: 0 0 10px rgba(0, 183, 255, 0.3);
        }

        .upload-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      `}</style>
    </motion.div>
  );
};
