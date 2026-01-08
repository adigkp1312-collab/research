/**
 * API Service
 * 
 * Backend API communication.
 * 
 * Team: Frontend
 */

import { CONFIG } from '../config';

export const chatApi = {
  /**
   * Stream chat response from backend.
   */
  async streamChat(
    message: string,
    sessionId: string,
    onChunk: (chunk: string) => void,
  ): Promise<void> {
    const response = await fetch(`${CONFIG.API_URL}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (reader) {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        onChunk(chunk);
      }
    }
  },

  /**
   * Non-streaming chat request.
   */
  async chat(message: string, sessionId: string): Promise<string> {
    const response = await fetch(`${CONFIG.API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data.response;
  },

  /**
   * Clear session memory.
   */
  async clearSession(sessionId: string): Promise<void> {
    await fetch(`${CONFIG.API_URL}/chat/session/${sessionId}`, {
      method: 'DELETE',
    });
  },

  /**
   * Health check.
   */
  async health(): Promise<{ status: string }> {
    const response = await fetch(`${CONFIG.API_URL}/health`);
    return response.json();
  },
};

export default chatApi;
