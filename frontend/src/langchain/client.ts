/**
 * LangChain Client Configuration
 * 
 * Configures ChatOpenAI to use OpenRouter for multi-model access.
 * OpenRouter provides a unified API for Gemini, Claude, GPT-4, and more.
 */

import { ChatOpenAI } from "@langchain/openai";

// Available models via OpenRouter
export const MODELS = {
  // Google Gemini models
  GEMINI_FLASH: "google/gemini-flash-1.5",
  GEMINI_PRO: "google/gemini-pro-1.5",
  
  // Anthropic Claude models
  CLAUDE_SONNET: "anthropic/claude-3-sonnet-20240229",
  CLAUDE_OPUS: "anthropic/claude-3-opus-20240229",
  
  // OpenAI models
  GPT4_TURBO: "openai/gpt-4-turbo",
  GPT4O: "openai/gpt-4o",
  
  // Fast/cheap options
  MISTRAL_LARGE: "mistralai/mistral-large-latest",
  LLAMA_70B: "meta-llama/llama-3-70b-instruct",
} as const;

export type ModelId = typeof MODELS[keyof typeof MODELS];

interface CreateChatModelOptions {
  temperature?: number;
  streaming?: boolean;
  maxTokens?: number;
}

/**
 * Creates a LangChain ChatModel configured to use OpenRouter.
 * 
 * @param modelId - The OpenRouter model ID (e.g., "google/gemini-flash-1.5")
 * @param options - Configuration options
 * @returns A configured ChatOpenAI instance
 * 
 * @example
 * ```typescript
 * const model = createChatModel(MODELS.GEMINI_FLASH);
 * const response = await model.invoke("Hello!");
 * ```
 */
export const createChatModel = (
  modelId: ModelId = MODELS.GEMINI_FLASH,
  options: CreateChatModelOptions = {}
): ChatOpenAI => {
  const {
    temperature = 0.7,
    streaming = true,
    maxTokens,
  } = options;

  // Get API key from environment
  const apiKey = import.meta.env.VITE_OPENROUTER_API_KEY;
  
  if (!apiKey) {
    console.warn("[LangChain] VITE_OPENROUTER_API_KEY not set. API calls will fail.");
  }

  return new ChatOpenAI({
    modelName: modelId,
    temperature,
    streaming,
    maxTokens,
    openAIApiKey: apiKey,
    configuration: {
      baseURL: "https://openrouter.ai/api/v1",
      defaultHeaders: {
        "HTTP-Referer": "https://adiyogi.art",
        "X-Title": "Adiyogi POC",
      },
    },
  });
};

/**
 * Quick helper to get a fast model for simple tasks
 */
export const getFastModel = (options?: CreateChatModelOptions) => 
  createChatModel(MODELS.GEMINI_FLASH, options);

/**
 * Quick helper to get a reasoning model for complex tasks
 */
export const getReasoningModel = (options?: CreateChatModelOptions) => 
  createChatModel(MODELS.GEMINI_PRO, options);

/**
 * Quick helper to get a creative model for writing tasks
 */
export const getCreativeModel = (options?: CreateChatModelOptions) => 
  createChatModel(MODELS.CLAUDE_SONNET, options);
