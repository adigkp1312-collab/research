/**
 * LangChain Client Configuration
 * 
 * Frontend client for backend API.
 * Actual LLM calls are handled by the backend which uses
 * GEMINI_API_KEY from Lambda environment variables.
 * 
 * This file is kept for compatibility but the frontend
 * doesn't make direct LLM calls anymore.
 */

// Model info (for display purposes)
export const CURRENT_MODEL = "gemini-2.0-flash-exp";
export const MODEL_NAME = "Gemini 3 Flash (Experimental)";

// Note: All LLM calls go through the backend API
// The backend reads GEMINI_API_KEY from Lambda environment variables
