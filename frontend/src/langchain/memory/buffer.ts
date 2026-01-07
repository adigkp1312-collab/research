/**
 * Memory Management for LangChain Conversations
 * 
 * Provides conversation memory that maintains context across chat turns.
 */

import { BufferWindowMemory } from "langchain/memory";
import { ChatMessageHistory } from "langchain/stores/message/in_memory";

// Store session memories (in production, use Redis or database)
const sessionMemories = new Map<string, BufferWindowMemory>();

/**
 * Creates or retrieves a BufferWindowMemory for a session.
 * 
 * BufferWindowMemory keeps the last K messages in context,
 * which is ideal for chat applications with limited context windows.
 * 
 * @param sessionId - Unique session identifier
 * @param windowSize - Number of messages to keep (default: 10)
 * @returns BufferWindowMemory instance
 */
export const getSessionMemory = (
  sessionId: string,
  windowSize: number = 10
): BufferWindowMemory => {
  // Return existing memory if available
  if (sessionMemories.has(sessionId)) {
    return sessionMemories.get(sessionId)!;
  }

  // Create new memory for this session
  const memory = new BufferWindowMemory({
    k: windowSize,
    returnMessages: true,
    memoryKey: "history",
    chatHistory: new ChatMessageHistory(),
  });

  sessionMemories.set(sessionId, memory);
  return memory;
};

/**
 * Clears memory for a specific session.
 * 
 * @param sessionId - Session to clear
 */
export const clearSessionMemory = (sessionId: string): void => {
  sessionMemories.delete(sessionId);
};

/**
 * Clears all session memories.
 * Useful for cleanup or testing.
 */
export const clearAllMemories = (): void => {
  sessionMemories.clear();
};

/**
 * Gets the number of active sessions.
 * 
 * @returns Count of sessions with active memory
 */
export const getActiveSessionCount = (): number => {
  return sessionMemories.size;
};
