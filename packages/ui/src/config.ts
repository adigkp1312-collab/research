/**
 * UI Configuration
 * 
 * Frontend configuration for the chat UI.
 * 
 * Team: Frontend
 */

export const CONFIG = {
    // Backend API URL (Cloud Run / Local development)
    API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8001',
    
    // Model Configuration
    MODELS: {
        GEMINI: {
            CHAT: 'gemini-2.5-flash',
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
