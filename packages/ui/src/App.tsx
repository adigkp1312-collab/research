/**
 * Main App Component
 * 
 * Team: Frontend
 */

import React, { useState } from 'react';
import { Header, Footer } from './components/Layout';
import { ChatContainer } from './components/Chat';

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    maxWidth: '900px',
    margin: '0 auto',
    padding: '0 20px',
  },
  chatWrapper: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
};

function App() {
  const [sessionId] = useState(() => `session-${Date.now()}`);

  return (
    <div style={styles.container}>
      <Header />
      <div style={styles.chatWrapper}>
        <ChatContainer sessionId={sessionId} />
      </div>
      <Footer sessionId={sessionId} />
    </div>
  );
}

export default App;
