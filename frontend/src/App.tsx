import React, { useState, useRef, useEffect } from 'react';
import { MODELS, type ModelId } from './langchain';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState<ModelId>(MODELS.GEMINI_FLASH);
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Add placeholder for assistant message
    const assistantId = `msg-${Date.now() + 1}`;
    setMessages(prev => [...prev, {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    }]);

    try {
      // Call backend streaming endpoint
      const response = await fetch(`${API_URL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: sessionId,
          model_id: selectedModel,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        let fullContent = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          fullContent += chunk;
          
          // Update the assistant message with streamed content
          setMessages(prev => prev.map(msg => 
            msg.id === assistantId 
              ? { ...msg, content: fullContent }
              : msg
          ));
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => prev.map(msg => 
        msg.id === assistantId 
          ? { ...msg, content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}` }
          : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <h1 style={styles.title}>LangChain Chat POC</h1>
        <div style={styles.modelSelector}>
          <label style={styles.label}>Model:</label>
          <select 
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value as ModelId)}
            style={styles.select}
          >
            <optgroup label="Google Gemini">
              <option value={MODELS.GEMINI_FLASH}>Gemini Flash (Fast)</option>
              <option value={MODELS.GEMINI_PRO}>Gemini Pro (Reasoning)</option>
            </optgroup>
            <optgroup label="Anthropic Claude">
              <option value={MODELS.CLAUDE_SONNET}>Claude Sonnet (Creative)</option>
              <option value={MODELS.CLAUDE_OPUS}>Claude Opus (Best)</option>
            </optgroup>
            <optgroup label="OpenAI">
              <option value={MODELS.GPT4_TURBO}>GPT-4 Turbo</option>
              <option value={MODELS.GPT4O}>GPT-4o</option>
            </optgroup>
          </select>
        </div>
      </header>

      {/* Messages */}
      <div style={styles.messages}>
        {messages.length === 0 && (
          <div style={styles.emptyState}>
            <h2 style={styles.emptyTitle}>Welcome to Adiyogi POC</h2>
            <p style={styles.emptyText}>
              This is a proof-of-concept for LangChain + OpenRouter integration.
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

      {/* Input */}
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

      {/* Footer */}
      <footer style={styles.footer}>
        <span>Session: {sessionId}</span>
        <span>•</span>
        <span>Model: {selectedModel}</span>
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
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    maxWidth: '900px',
    margin: '0 auto',
    padding: '0 20px',
  },
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
  modelSelector: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  label: {
    fontSize: '14px',
    color: '#888',
  },
  select: {
    padding: '8px 12px',
    fontSize: '14px',
    backgroundColor: '#1a1a1a',
    color: '#e0e0e0',
    border: '1px solid #333',
    borderRadius: '6px',
    cursor: 'pointer',
  },
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

export default App;
