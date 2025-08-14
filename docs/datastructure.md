# Data Structure and Persistence Design (MongoDB)

## Goals
- Persist speaking test sessions with level, timestamps, and status.
- Enable resuming in-progress sessions and reviewing past sessions (recordings, transcripts, evaluations).
- Keep the app portable for dev (local MongoDB) and cloud (managed Mongo).

## MongoDB Setup
- URI: `MONGODB_URI` (default: `mongodb://localhost:27017`)
- DB: `MONGODB_DB` (default: `speak_check`)
- Client: `pymongo`

## Collections

### users (optional)
```
{
  _id: ObjectId,
  email: string?,
  name: string?,
  created_at: Date
}
```

### sessions
```
{
  _id: ObjectId,
  user_id: ObjectId | null,
  level: 'A2'|'B1'|'B2'|'C1',
  status: 'active'|'completed'|'abandoned',
  started_at: Date,
  ended_at: Date | null,
  metadata: object | null
}
```
Indexes:
- { user_id: 1, started_at: -1 }
- { status: 1 }

### recordings
```
{
  _id: ObjectId,
  session_id: ObjectId,
  file_url: string,           // path or S3 URL
  duration_s: number?,
  sample_rate: number?,
  channels: number,           // default 1
  created_at: Date
}
```
Indexes:
- { session_id: 1, created_at: -1 }

### transcripts
```
{
  _id: ObjectId,
  recording_id: ObjectId,
  text: string,
  language: string,
  provider: string,           // 'openai'
  model: string,              // 'whisper-1'
  segments: array?,
  created_at: Date
}
```
Indexes:
- { recording_id: 1 }

### evaluations
```
{
  _id: ObjectId,
  transcript_id: ObjectId,
  overall_level: 'A2'|'B1'|'B2'|'C1',
  confidence: number,         // 0..1
  scores: object,             // {fluency, accuracy, grammar, vocabulary, coherence}
  rationale: string,
  tips: array,
  created_at: Date
}
```
Indexes:
- { transcript_id: 1 }

### events (audit/analytics)
```
{
  _id: ObjectId,
  session_id: ObjectId,
  type: string,               // 'start'|'record_stop'|'transcribe'|'evaluate'
  payload: object?,
  created_at: Date
}
```
Indexes:
- { session_id: 1, created_at: 1 }

## UI Integration Flow
- Start Speaking Test → insert `sessions`; store `_id` in `st.session_state.test_session_id`.
- Stop Recording → insert `recordings` with file path and duration.
- Transcribe → insert `transcripts` with text and metadata.
- Evaluate → insert `evaluations` with scores and rationale.
- History sidebar → `list_sessions()` → select → resume by setting `test_session_id`, `current_level`, `test_started=True`.

## Decisions
- Audio blobs stay on disk/S3; DB stores metadata. GridFS optional if you must store blobs.
- Consistent timestamps in UTC.
- Keep writes lean; avoid PII where possible.

## Next Steps
- Add creation of indexes on first run.
- Add a simple History panel to navigate sessions.
- Add delete/prune utilities for old audio while keeping metadata.
