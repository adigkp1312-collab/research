/**
 * Conversation Chain Implementation
 * 
 * Creates a conversation chain with memory for the Director AI chat.
 * This replaces the custom chatIntelligence.ts and related files.
 */

import { ConversationChain } from "langchain/chains";
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";
import { createChatModel, MODELS, type ModelId } from "../client";
import { getSessionMemory } from "../memory/buffer";

// Director system prompt - customize as needed
const DIRECTOR_SYSTEM_PROMPT = `You are a creative director for short-form video production at Adiyogi Arts.

Your role is to help users brainstorm, develop, and refine video concepts. You specialize in:
- Story development and narrative structure
- Visual storytelling and shot composition
- Character development and dialogue
- Mood, tone, and emotional themes
- Indian mythology and cultural elements

Guidelines:
1. Be creative but practical - suggestions should be achievable
2. Ask clarifying questions to understand the user's vision
3. Offer specific, actionable suggestions
4. Consider the target audience and platform
5. Balance artistic vision with production constraints

Keep responses concise and focused. When appropriate, structure your output for easy parsing.`;

interface DirectorChainOptions {
  sessionId: string;
  modelId?: ModelId;
  systemPrompt?: string;
  windowSize?: number;
}

/**
 * Creates a Director conversation chain with memory.
 * 
 * @param options - Configuration options
 * @returns ConversationChain with memory
 * 
 * @example
 * ```typescript
 * const chain = createDirectorChain({ sessionId: "user-123" });
 * const response = await chain.invoke({ input: "Help me brainstorm a video about Hanuman" });
 * console.log(response.response);
 * ```
 */
export const createDirectorChain = (options: DirectorChainOptions): ConversationChain => {
  const {
    sessionId,
    modelId = MODELS.GEMINI_FLASH,
    systemPrompt = DIRECTOR_SYSTEM_PROMPT,
    windowSize = 10,
  } = options;

  // Create the chat model
  const model = createChatModel(modelId, {
    temperature: 0.7,
    streaming: true,
  });

  // Create the prompt template with system message and history
  const prompt = ChatPromptTemplate.fromMessages([
    ["system", systemPrompt],
    new MessagesPlaceholder("history"),
    ["human", "{input}"],
  ]);

  // Get or create memory for this session
  const memory = getSessionMemory(sessionId, windowSize);

  // Create and return the conversation chain
  return new ConversationChain({
    llm: model,
    prompt,
    memory,
    verbose: import.meta.env.DEV, // Enable verbose logging in development
  });
};

/**
 * Simple wrapper for quick chat without creating a chain manually.
 * 
 * @param sessionId - Session identifier
 * @param message - User message
 * @param modelId - Optional model override
 * @returns AI response text
 */
export const quickChat = async (
  sessionId: string,
  message: string,
  modelId?: ModelId
): Promise<string> => {
  const chain = createDirectorChain({ sessionId, modelId });
  const result = await chain.invoke({ input: message });
  return result.response as string;
};

/**
 * Streaming chat that yields tokens as they arrive.
 * 
 * @param sessionId - Session identifier
 * @param message - User message
 * @param onToken - Callback for each token
 * @param modelId - Optional model override
 */
export const streamChat = async (
  sessionId: string,
  message: string,
  onToken: (token: string) => void,
  modelId?: ModelId
): Promise<string> => {
  const chain = createDirectorChain({ sessionId, modelId });
  
  let fullResponse = "";
  
  // Use streaming with callbacks
  const result = await chain.invoke(
    { input: message },
    {
      callbacks: [
        {
          handleLLMNewToken(token: string) {
            fullResponse += token;
            onToken(token);
          },
        },
      ],
    }
  );

  return result.response as string;
};
