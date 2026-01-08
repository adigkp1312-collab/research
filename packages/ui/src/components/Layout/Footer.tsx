/**
 * Footer Component
 * 
 * Application footer with session info.
 * 
 * Team: Frontend
 */

import React from 'react';

const styles: Record<string, React.CSSProperties> = {
  footer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '12px',
    padding: '16px 0',
    fontSize: '12px',
    color: '#666',
  },
  link: {
    color: '#ff6b6b',
    textDecoration: 'none',
  },
};

interface FooterProps {
  sessionId: string;
}

export const Footer: React.FC<FooterProps> = ({ sessionId }) => {
  return (
    <footer style={styles.footer}>
      <span>Session: {sessionId}</span>
      <span>•</span>
      <span>Model: Gemini 3 Flash</span>
      <span>•</span>
      <a 
        href="https://smith.langchain.com" 
        target="_blank" 
        rel="noopener noreferrer"
        style={styles.link}
      >
        View Traces in LangSmith →
      </a>
    </footer>
  );
};

export default Footer;
