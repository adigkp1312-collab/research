/**
 * MessageList Component
 * 
 * Displays list of chat messages.
 * 
 * Team: Frontend
 */

import React, { useRef, useEffect } from 'react';
import { Message, MessageListProps } from './types';

const styles: Record<string, React.CSSProperties> = {
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '20px 0',
  },
  emptyState: {
    textAlign: 'center',
    padding: '60px 20px',
  },
  emptyTitle: {
    fontSize: '28px',
    fontWeight: '600',
    marginBottom: '12px',
    color: '#fff',
  },
  emptyText: {
    fontSize: '16px',
    color: '#888',
    maxWidth: '500px',
    margin: '0 auto',
    lineHeight: '1.6',
  },
  message: {
    marginBottom: '16px',
    padding: '16px',
    borderRadius: '12px',
  },
  userMessage: {
    backgroundColor: '#1a3a5c',
    marginLeft: '40px',
  },
  assistantMessage: {
    backgroundColor: '#1a1a1a',
    marginRight: '40px',
    border: '1px solid #333',
  },
  messageRole: {
    fontSize: '12px',
    fontWeight: '600',
    marginBottom: '8px',
    color: '#888',
  },
  messageContent: {
    fontSize: '15px',
    lineHeight: '1.6',
    whiteSpace: 'pre-wrap',
  },
};

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div style={styles.messages}>
      {messages.length === 0 && (
        <div style={styles.emptyState}>
          <h2 style={styles.emptyTitle}>Welcome to Adiyogi POC</h2>
          <p style={styles.emptyText}>
            This is a proof-of-concept for LangChain + Gemini 3 Flash integration.
            Try asking about video production, storytelling, or Indian mythology.
          </p>
        </div>
      )}
      {messages.map(message => (
        <div 
          key={message.id}
          style={{
            ...styles.message,
            ...(message.role === 'user' ? styles.userMessage : styles.assistantMessage),
          }}
        >
          <div style={styles.messageRole}>
            {message.role === 'user' ? '👤 You' : '🎬 Director'}
          </div>
          <div style={styles.messageContent}>
            {message.content || (isLoading ? '...' : '')}
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
