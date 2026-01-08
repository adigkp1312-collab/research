/**
 * Header Component
 * 
 * Application header with title and model info.
 * 
 * Team: Frontend
 */

import React from 'react';

const styles: Record<string, React.CSSProperties> = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 0',
    borderBottom: '1px solid #333',
  },
  title: {
    fontSize: '24px',
    fontWeight: '600',
    background: 'linear-gradient(135deg, #ff6b6b, #ffd93d)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  modelInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  modelBadge: {
    padding: '8px 16px',
    fontSize: '14px',
    backgroundColor: '#1a3a5c',
    color: '#4fc3f7',
    border: '1px solid #333',
    borderRadius: '6px',
    fontWeight: '600',
  },
};

interface HeaderProps {
  title?: string;
  modelName?: string;
}

export const Header: React.FC<HeaderProps> = ({ 
  title = 'LangChain Chat POC',
  modelName = 'Gemini 3 Flash',
}) => {
  return (
    <header style={styles.header}>
      <h1 style={styles.title}>{title}</h1>
      <div style={styles.modelInfo}>
        <span style={styles.modelBadge}>{modelName}</span>
      </div>
    </header>
  );
};

export default Header;
