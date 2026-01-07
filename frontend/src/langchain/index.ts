/**
 * LangChain Module Entry Point
 * 
 * Re-exports all LangChain utilities for easy importing.
 */

// Client and models
export { 
  createChatModel, 
  getFastModel, 
  getReasoningModel, 
  getCreativeModel,
  MODELS,
  type ModelId 
} from "./client";

// Memory management
export { 
  getSessionMemory, 
  clearSessionMemory, 
  clearAllMemories,
  getActiveSessionCount 
} from "./memory/buffer";

// Chains
export { 
  createDirectorChain, 
  quickChat, 
  streamChat 
} from "./chains/conversation";
