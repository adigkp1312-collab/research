/**
 * useChat Hook
 * 
 * Manages chat state and API communication.
 * 
 * Team: Frontend
 */

import { useState, useCallback } from 'react';
import { Message } from '../components/Chat/types';
import { chatApi } from '../services/api';

export const useChat = (initialSessionId?: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => initialSessionId || `session-${Date.now()}`);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
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
      // Use non-streaming endpoint (streaming not fully supported in Lambda yet)
      const response = await chatApi.chat(userMessage.content, sessionId);
      setMessages(prev => prev.map(msg => 
        msg.id === assistantId 
          ? { ...msg, content: response }
          : msg
      ));
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
  }, [sessionId, isLoading]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isLoading,
    sessionId,
    sendMessage,
    clearMessages,
  };
};

export default useChat;
