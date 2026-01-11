# Pending Implementation Items - Priority Order

> **Last Updated**: January 2026  
> **Status**: Phase 0 Complete ✅

---

## Priority 1: Complete RAG System Foundation (Critical Path)

### P1.1: Update File Processor Integration
**Priority**: HIGH  
**Estimated Time**: 2-3 hours  
**File**: `packages/knowledge_base/src/processor.py`

- [ ] Update `process_file()` to use `MetadataStore` for tracking
- [ ] Integrate with `DatastoreManager` for document import
- [ ] Add proper error handling and status updates
- [ ] Remove deprecated `vertexai.preview.rag` imports
- [ ] Update to use new `FileMetadata` model

**Dependencies**: Phase 0 complete ✅

---

### P1.2: Create Datastore API Routes
**Priority**: HIGH  
**Estimated Time**: 3-4 hours  
**File**: `packages/api/src/routes/datastore.py` (NEW)

- [ ] Create file upload endpoint (`POST /datastore/files`)
- [ ] Create file list endpoint (`GET /datastore/files`)
- [ ] Create file metadata endpoint (`GET /datastore/files/{file_id}`)
- [ ] Create file delete endpoint (`DELETE /datastore/files/{file_id}`)
- [ ] Create search endpoint (`POST /datastore/search`)
- [ ] Create stats endpoint (`GET /datastore/stats`)
- [ ] Create datastore info endpoint (`GET /datastore`)

**Dependencies**: P1.1

---

### P1.3: Integrate RAG into Chat Director
**Priority**: HIGH  
**Estimated Time**: 1-2 hours  
**File**: `packages/langchain_chains/src/director.py`

- [ ] Add `_get_rag_context()` function
- [ ] Update `_build_conversation_prompt()` to accept RAG context
- [ ] Modify `stream_chat()` to retrieve context before generation
- [ ] Modify `quick_chat()` to retrieve context before generation
- [ ] Add graceful degradation if RAG fails

**Dependencies**: P1.1

---

### P1.4: Update API App Configuration
**Priority**: MEDIUM  
**Estimated Time**: 30 minutes  
**File**: `packages/api/src/app.py`

- [ ] Import `datastore_router`
- [ ] Add router to app includes
- [ ] Update `packages/api/src/routes/__init__.py` exports

**Dependencies**: P1.2

---

## Priority 2: Testing & Validation

### P2.1: Unit Tests for Knowledge Base
**Priority**: MEDIUM  
**Estimated Time**: 4-5 hours  
**Files**: `packages/knowledge_base/tests/`

- [ ] `test_metadata.py` - Test MetadataStore operations
- [ ] `test_datastore.py` - Test DatastoreManager (with mocks)
- [ ] `test_retriever.py` - Test RAGRetriever (with mocks)
- [ ] `test_processor.py` - Test file processing pipeline
- [ ] `conftest.py` - Shared fixtures

**Dependencies**: P1.1

---

### P2.2: Integration Tests
**Priority**: MEDIUM  
**Estimated Time**: 2-3 hours  
**Files**: `packages/api/tests/`

- [ ] Test datastore routes with mock services
- [ ] Test RAG integration in chat flow
- [ ] Test file upload end-to-end (mock GCS)

**Dependencies**: P1.2, P1.3

---

## Priority 3: Frontend UI (RAG System)

### P3.1: Datastore API Service
**Priority**: MEDIUM  
**Estimated Time**: 1-2 hours  
**File**: `packages/ui/src/services/datastoreApi.ts` (NEW)

- [ ] Create TypeScript interfaces for API models
- [ ] Implement `uploadFile()`, `listFiles()`, `getFile()`, `deleteFile()`
- [ ] Implement `searchDatastore()`, `getDatastoreInfo()`, `getStats()`
- [ ] Add error handling

**Dependencies**: P1.2

---

### P3.2: File Upload Component
**Priority**: MEDIUM  
**Estimated Time**: 2-3 hours  
**File**: `packages/ui/src/components/Datastore/FileUpload.tsx` (NEW)

- [ ] Drag-and-drop file upload
- [ ] File type validation
- [ ] Upload progress indicator
- [ ] Error handling and display

**Dependencies**: P3.1

---

### P3.3: File List Component
**Priority**: MEDIUM  
**Estimated Time**: 2-3 hours  
**File**: `packages/ui/src/components/Datastore/FileList.tsx` (NEW)

- [ ] Table/grid view of files
- [ ] Status badges (pending, indexed, failed)
- [ ] Filter by status/file type
- [ ] Pagination
- [ ] Delete action

**Dependencies**: P3.1

---

### P3.4: Datastore Dashboard
**Priority**: LOW  
**Estimated Time**: 2-3 hours  
**File**: `packages/ui/src/components/Datastore/DatastoreDashboard.tsx` (NEW)

- [ ] Combine FileUpload and FileList
- [ ] Add stats display
- [ ] Add search panel
- [ ] Add navigation/routing

**Dependencies**: P3.2, P3.3

---

## Priority 4: Video Processing Service

### P4.1: Core Data Models
**Priority**: MEDIUM  
**Estimated Time**: 1-2 hours  
**File**: `packages/video_processing/src/models.py` (NEW)

- [ ] Create all data classes (ProcessedVideo, VideoMetadata, etc.)
- [ ] Create enums (ProcessingStatus, OutputType, PromptStyle)
- [ ] Add model configurations and pricing

**Dependencies**: None (can start in parallel)

---

### P4.2: Configuration & Prompts
**Priority**: MEDIUM  
**Estimated Time**: 1-2 hours  
**Files**: 
- `packages/video_processing/src/config.py` (NEW)
- `packages/video_processing/src/prompts.py` (NEW)

- [ ] Create ProcessingConfig and OutputConfig classes
- [ ] Create preset configurations
- [ ] Create prompt templates for different styles

**Dependencies**: P4.1

---

### P4.3: Transcript Extraction
**Priority**: MEDIUM  
**Estimated Time**: 2-3 hours  
**File**: `packages/video_processing/src/transcript.py` (NEW)

- [ ] Implement `extract_video_id()` with URL parsing
- [ ] Implement `get_video_metadata()` with rate limiting
- [ ] Implement `fetch_transcript()` with fallback logic
- [ ] Add error handling

**Dependencies**: P4.1

---

### P4.4: LLM Client with Retry
**Priority**: MEDIUM  
**Estimated Time**: 2-3 hours  
**File**: `packages/video_processing/src/llm.py` (NEW)

- [ ] Create GeminiClient class
- [ ] Add retry logic with tenacity
- [ ] Add cost tracking and limits
- [ ] Support both Vertex AI and direct API

**Dependencies**: P4.1

---

### P4.5: Summarizer Module
**Priority**: MEDIUM  
**Estimated Time**: 2-3 hours  
**File**: `packages/video_processing/src/summarizer.py` (NEW)

- [ ] Implement `generate_summary()` with prompt styles
- [ ] Implement `extract_speakers()`
- [ ] Implement `generate_qa()`
- [ ] Add proper error handling

**Dependencies**: P4.2, P4.4

---

### P4.6: TTS Generator
**Priority**: LOW  
**Estimated Time**: 1-2 hours  
**File**: `packages/video_processing/src/tts.py` (NEW)

- [ ] Implement `generate_speech()` using Gemini TTS API
- [ ] Implement `generate_audio_summary()` with WAV conversion
- [ ] Add voice selection and language support

**Dependencies**: P4.1

---

### P4.7: Main Processor Orchestrator
**Priority**: MEDIUM  
**Estimated Time**: 3-4 hours  
**File**: `packages/video_processing/src/processor.py` (NEW)

- [ ] Create VideoProcessor class
- [ ] Implement `process_video()` pipeline
- [ ] Add progress tracking callbacks
- [ ] Integrate all modules (transcript, summary, Q&A, TTS)
- [ ] Add cost tracking

**Dependencies**: P4.3, P4.5, P4.6

---

### P4.8: Video Processing API Routes
**Priority**: LOW  
**Estimated Time**: 2-3 hours  
**File**: `packages/api/src/routes/video.py` (NEW)

- [ ] Create `POST /video/process` endpoint
- [ ] Create `GET /video/jobs/{job_id}` endpoint
- [ ] Create `GET /video/processed/{video_id}` endpoint
- [ ] Add background task handling

**Dependencies**: P4.7

---

### P4.9: RAG Integration for Videos
**Priority**: LOW  
**Estimated Time**: 1-2 hours  
**File**: `packages/video_processing/src/rag_integration.py` (NEW)

- [ ] Implement `ingest_video_to_knowledge_base()`
- [ ] Format transcript, summary, Q&A for ingestion
- [ ] Integrate with knowledge base processor

**Dependencies**: P4.7, P1.1

---

## Priority 5: Documentation & Polish

### P5.1: Update README Files
**Priority**: LOW  
**Estimated Time**: 1-2 hours

- [ ] Update `packages/knowledge_base/README.md` with usage examples
- [ ] Create `packages/video_processing/README.md`
- [ ] Update main project README with new features

**Dependencies**: P1.1, P4.7

---

### P5.2: Environment Variables Documentation
**Priority**: LOW  
**Estimated Time**: 30 minutes

- [ ] Document all required env vars in `.env.example`
- [ ] Add validation checks
- [ ] Update setup documentation

**Dependencies**: All phases

---

## Summary by Priority

| Priority | Items | Estimated Time | Status |
|----------|-------|----------------|--------|
| **P1** (Critical) | 4 items | 7-10 hours | Ready to start |
| **P2** (Testing) | 2 items | 6-8 hours | After P1 |
| **P3** (Frontend) | 4 items | 7-11 hours | After P1 |
| **P4** (Video) | 9 items | 16-24 hours | Can parallelize |
| **P5** (Docs) | 2 items | 1.5-2.5 hours | Final |

**Total Estimated Time**: 37-55 hours

---

## Recommended Implementation Order

1. **Week 1**: Complete P1.1 → P1.2 → P1.3 → P1.4 (RAG foundation)
2. **Week 2**: P2.1 → P2.2 (Testing) + P3.1 → P3.2 → P3.3 (Frontend basics)
3. **Week 3**: P4.1 → P4.2 → P4.3 → P4.4 → P4.5 (Video core)
4. **Week 4**: P4.6 → P4.7 → P4.8 → P4.9 (Video completion)
5. **Week 5**: P3.4 + P5.1 + P5.2 (Polish & docs)

---

## Blockers & Dependencies

- **P1.2** requires **P1.1** (processor must work before API)
- **P1.3** requires **P1.1** (RAG retrieval needs working retriever)
- **P2.1** requires **P1.1** (test what's implemented)
- **P3.x** requires **P1.2** (UI needs API endpoints)
- **P4.7** requires P4.3, P4.5, P4.6 (orchestrator needs modules)
- **P4.9** requires **P4.7** + **P1.1** (integration needs both systems)

---

## Quick Wins (Can Do First)

- ✅ **Phase 0** - Already complete
- **P4.1** - Video models (independent, can start now)
- **P4.2** - Video config/prompts (independent)
- **P5.2** - Env var docs (independent)
