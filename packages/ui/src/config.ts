/**
 * UI Configuration
 * 
 * Frontend configuration for the chat UI.
 * 
 * Team: Frontend
 */

export const CONFIG = {
    // Backend API URL
    API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    
    // Gemini API Key (optional - for direct frontend calls)
    GEMINI_API_KEY: import.meta.env.VITE_GEMINI_API_KEY || '',
    
    // Model Configuration
    MODELS: {
        GEMINI: {
            CHAT: 'gemini-2.0-flash-exp',
        },
    },
} as const;

/**
 * Validate configuration
 */
export const validateConfig = (): { valid: boolean; missing: string[] } => {
    const missing: string[] = [];
    
    if (!CONFIG.API_URL) {
        missing.push('VITE_API_URL');
    }
    
    if (missing.length > 0) {
        console.warn('[Config] Missing:', missing);
    }
    
    return { valid: missing.length === 0, missing };
};

export default CONFIG;
