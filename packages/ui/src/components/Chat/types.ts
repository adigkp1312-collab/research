/**
 * Chat Component Types
 * 
 * Team: Frontend
 */

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatContainerProps {
  sessionId?: string;
}

export interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export interface InputFormProps {
  onSubmit: (message: string) => void;
  isLoading: boolean;
}
