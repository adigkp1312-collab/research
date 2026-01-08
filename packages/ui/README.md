# UI Package

**Team:** Frontend

React frontend for the LangChain chat application.

## Contents

- `src/components/` - React components
  - `Chat/` - Chat components (ChatContainer, MessageList, InputForm)
  - `Layout/` - Layout components (Header, Footer)
- `src/hooks/` - Custom React hooks
  - `useChat.ts` - Chat state management
- `src/services/` - API services
  - `api.ts` - Backend API client
- `src/config.ts` - Frontend configuration

## Usage

```bash
cd packages/ui
npm install
npm run dev
```

## Components

### ChatContainer
Main chat component with messages and input:

```tsx
import { ChatContainer } from './components/Chat';

<ChatContainer sessionId="user-123" />
```

### useChat Hook
Manages chat state:

```tsx
import { useChat } from './hooks/useChat';

const { messages, isLoading, sendMessage } = useChat();
```

## Configuration

Set environment variables in `.env`:

```env
VITE_API_URL=http://localhost:8000
```

## Testing

```bash
npm run test
```
