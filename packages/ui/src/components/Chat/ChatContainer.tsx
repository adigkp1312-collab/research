/**
 * ChatContainer Component
 * 
 * Main chat container with message list and input.
 * 
 * Team: Frontend
 */

import React from 'react';
import { ChatContainerProps } from './types';
import { MessageList } from './MessageList';
import { InputForm } from './InputForm';
import { useChat } from '../../hooks/useChat';

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
  },
};

export const ChatContainer: React.FC<ChatContainerProps> = ({ sessionId }) => {
  const { messages, isLoading, sendMessage } = useChat(sessionId);

  return (
    <div style={styles.container}>
      <MessageList messages={messages} isLoading={isLoading} />
      <InputForm onSubmit={sendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatContainer;
