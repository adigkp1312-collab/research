/**
 * Centralized Configuration
 * 
 * Pattern matches main codebase: frontend/config.ts
 * Uses environment variables with sensible defaults
 */

/**
 * Main configuration object
 * Uses environment variables with sensible defaults
 */
export const CONFIG = {
    // Backend API URL
    API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    
    // Gemini API Key (optional - can be set in localStorage)
    GEMINI_API_KEY: import.meta.env.VITE_GEMINI_API_KEY || '',
    
    // Model Configuration
    MODELS: {
        GEMINI: {
            CHAT: 'gemini-2.0-flash-exp',  // Gemini 3 Flash
        },
    },
} as const;

/**
 * Validate that required configuration is present
 * Call this on app startup to catch missing config early
 */
export const validateConfig = (): { valid: boolean; missing: string[] } => {
    const missing: string[] = [];
    
    // API_URL is required for backend communication
    if (!CONFIG.API_URL) {
        missing.push('VITE_API_URL');
    }
    
    if (missing.length > 0) {
        console.warn('[Config] Missing required environment variables:', missing);
    }
    
    return { valid: missing.length === 0, missing };
};

export default CONFIG;
