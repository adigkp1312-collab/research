/**
 * LangChain Client Configuration
 * 
 * Frontend client for backend API.
 * Pattern matches main codebase: frontend/services/api/gemini/client.ts
 * 
 * Note: All LLM calls go through the backend API.
 * The backend reads GEMINI_API_KEY from Lambda environment variables.
 */

import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { CONFIG } from "../config";

// Model info (for display purposes)
export const CURRENT_MODEL = CONFIG.MODELS.GEMINI.CHAT;
export const MODEL_NAME = "Gemini 3 Flash (Experimental)";

/**
 * Creates a LangChain ChatModel for Gemini 3 Flash.
 * 
 * Pattern matches main codebase: frontend/services/api/gemini/client.ts
 * Reads VITE_GEMINI_API_KEY from environment variables.
 * 
 * Note: This is primarily for frontend display/testing.
 * Production LLM calls should go through the backend API.
 */
export const createChatModel = (
  temperature: number = 0.7,
  streaming: boolean = true,
  maxTokens?: number,
): ChatGoogleGenerativeAI => {
  // Direct access - matches main codebase pattern
  // Pattern: const ENV_API_KEY = import.meta.env.VITE_GEMINI_API_KEY || '';
  const apiKey = CONFIG.GEMINI_API_KEY || import.meta.env.VITE_GEMINI_API_KEY || '';
  
  if (!apiKey) {
    console.warn("[LangChain] VITE_GEMINI_API_KEY not set. API calls will fail.");
  }
  
  return new ChatGoogleGenerativeAI({
    model: CONFIG.MODELS.GEMINI.CHAT,
    temperature,
    streaming,
    maxOutputTokens: maxTokens,
    apiKey: apiKey,
  });
};

