# Chat Knowledge Base

**Last Updated:** 2024-01-08  
**Model:** Gemini 2.5 Flash (Vertex AI)

---

## 📚 Knowledge Sources

The chat system uses the following knowledge sources:

### 1. **Gemini 2.5 Flash Model Training Data**

The primary knowledge base is **Gemini 2.5 Flash's built-in training data**:

- ✅ **General Knowledge**: World knowledge up to the model's training cutoff date
- ✅ **Language Understanding**: Natural language processing capabilities
- ✅ **Reasoning**: Logical reasoning and problem-solving
- ✅ **Code Generation**: Programming languages and software development
- ✅ **Creative Writing**: Storytelling, poetry, and creative content
- ✅ **Cultural Knowledge**: Including Indian mythology and culture (relevant to Adiyogi Arts)

**Limitations:**
- ❌ **No Real-time Information**: Cannot access current events or recent information beyond training cutoff
- ❌ **No Custom Documents**: Does not have access to your specific documents or databases
- ❌ **No Internet Access**: Cannot browse the web or search for information

### 2. **System Prompts**

The system uses specialized prompts to guide the model's behavior:

#### **Director System Prompt** (Default)
- Role: Creative director for short-form video production
- Expertise: Story development, visual storytelling, character development, Indian mythology
- Focus: Practical, actionable suggestions for video production

#### **Assistant System Prompt**
- Role: General AI assistant
- Expertise: Video production, Indian mythology, creative storytelling, technical questions

#### **Brainstorm System Prompt**
- Role: Creative brainstorming partner
- Focus: Generating multiple ideas, exploring unconventional approaches

**Location:** `packages/langchain_chains/src/prompts.py`

### 3. **Conversation History**

The system maintains **session-based conversation memory**:

- **Window Size**: Last 10 message pairs (20 messages total)
- **Storage**: In-memory (per session)
- **Purpose**: Provides context for ongoing conversations
- **Scope**: Only within the same session ID

**Location:** `packages/langchain_memory/src/buffer.py`

---

## 🔍 What the Chat Does NOT Have

### ❌ No RAG (Retrieval Augmented Generation)
- No vector database integration
- No document embedding or retrieval
- No custom knowledge base search

### ❌ No Real-time Web Search
- The main chat does not use Google Search grounding
- Cannot fetch current information from the internet
- Cannot access live web content

### ❌ No Custom Knowledge Base
- No integration with company documents
- No access to proprietary databases
- No custom data sources

### ❌ No External APIs
- No integration with external knowledge APIs
- No Wikipedia or encyclopedia access
- No database queries

---

## 🔄 Research Agent (Separate Service)

**Note:** There is a **separate research agent service** (`apps/research-service`) that DOES have:

- ✅ **Google Search Grounding**: Real-time internet research
- ✅ **Current Information**: Access to up-to-date web content
- ✅ **Source URLs**: Returns verified sources

However, this is **not integrated** with the main chat system. It's a separate API endpoint.

**Location:** `packages/research_agent/`  
**Service:** `apps/research-service`

---

## 📊 Knowledge Base Summary

| Component | Status | Details |
|-----------|--------|---------|
| **Model Training Data** | ✅ Active | Gemini 2.5 Flash built-in knowledge |
| **System Prompts** | ✅ Active | Director, Assistant, Brainstorm personas |
| **Conversation Memory** | ✅ Active | Last 10 message pairs per session |
| **RAG/Vector DB** | ❌ Not Implemented | No custom knowledge retrieval |
| **Web Search** | ❌ Not Integrated | Available in research agent only |
| **Custom Documents** | ❌ Not Implemented | No document upload/ingestion |

---

## 💡 Use Cases

The chat is best suited for:

✅ **Creative Assistance**
- Video concept development
- Story brainstorming
- Character development
- Visual storytelling ideas

✅ **General Knowledge**
- Questions about topics in training data
- Code generation and debugging
- Writing assistance
- Cultural and mythological information

✅ **Conversational Context**
- Multi-turn conversations
- Building on previous messages
- Maintaining conversation flow

---

## 🚀 Future Enhancements (Potential)

If you need additional knowledge capabilities, consider:

1. **RAG Integration**
   - Vector database (e.g., Pinecone, Weaviate)
   - Document embedding and retrieval
   - Custom knowledge base search

2. **Google Search Grounding**
   - Integrate Google Search into main chat
   - Real-time information access
   - Current events and recent data

3. **Custom Knowledge Base**
   - Company document repository
   - Product catalogs
   - Internal wikis or documentation

4. **External API Integration**
   - Wikipedia API
   - News APIs
   - Specialized knowledge APIs

---

## 📝 Technical Details

### Model Configuration
- **Model**: `gemini-2.5-flash`
- **Provider**: Google Vertex AI
- **Location**: `us-central1`
- **Temperature**: 0.7 (default)
- **Streaming**: Supported

### Memory Configuration
- **Storage**: In-memory dictionary (`_session_memories`)
- **Window Size**: 10 message pairs (configurable)
- **Session Management**: Per-session isolation
- **Persistence**: Not persisted (lost on server restart)

### Prompt Construction
```
[System Prompt]
[Conversation History - Last 10 pairs]
[Current User Message]
[Assistant Response]
```

---

## 🔗 Related Documentation

- **Architecture**: `docs/architecture/LLM_FLOW.md`
- **Research Agent**: `RESEARCH_AGENT_ABILITIES.md`
- **Features**: `FEATURES.md`
- **System Prompts**: `packages/langchain_chains/src/prompts.py`
