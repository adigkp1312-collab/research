/**
 * InputForm Component
 * 
 * Chat input form with submit button.
 * 
 * Team: Frontend
 */

import React, { useState } from 'react';
import { InputFormProps } from './types';

const styles: Record<string, React.CSSProperties> = {
  inputForm: {
    display: 'flex',
    gap: '12px',
    padding: '20px 0',
    borderTop: '1px solid #333',
  },
  input: {
    flex: 1,
    padding: '14px 18px',
    fontSize: '15px',
    backgroundColor: '#1a1a1a',
    color: '#e0e0e0',
    border: '1px solid #333',
    borderRadius: '8px',
    outline: 'none',
  },
  button: {
    padding: '14px 28px',
    fontSize: '15px',
    fontWeight: '600',
    backgroundColor: '#ff6b6b',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  buttonDisabled: {
    backgroundColor: '#555',
    cursor: 'not-allowed',
  },
};

export const InputForm: React.FC<InputFormProps> = ({ onSubmit, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    onSubmit(input.trim());
    setInput('');
  };

  return (
    <form onSubmit={handleSubmit} style={styles.inputForm}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask about video production, storytelling..."
        style={styles.input}
        disabled={isLoading}
      />
      <button 
        type="submit" 
        style={{
          ...styles.button,
          ...(isLoading ? styles.buttonDisabled : {}),
        }}
        disabled={isLoading}
      >
        {isLoading ? 'Thinking...' : 'Send'}
      </button>
    </form>
  );
};

export default InputForm;
