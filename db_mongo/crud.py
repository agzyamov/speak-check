from datetime import datetime
from bson import ObjectId
from .client import db

# Sessions

def create_session(level: str, user_id: str | None = None) -> str:
    doc = {
        "user_id": ObjectId(user_id) if user_id else None,
        "level": level,
        "status": "active",
        "started_at": datetime.utcnow(),
        "ended_at": None,
        "metadata": None,
    }
    res = db.sessions.insert_one(doc)
    return str(res.inserted_id)


def end_session(session_id: str, status: str = "completed") -> None:
    db.sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"status": status, "ended_at": datetime.utcnow()}},
    )


# Recordings

def add_recording(
    session_id: str,
    file_url: str,
    duration_s: float | None = None,
    sample_rate: int | None = None,
    channels: int = 1,
) -> str:
    res = db.recordings.insert_one(
        {
            "session_id": ObjectId(session_id),
            "file_url": file_url,
            "duration_s": duration_s,
            "sample_rate": sample_rate,
            "channels": channels,
            "created_at": datetime.utcnow(),
        }
    )
    return str(res.inserted_id)


# Transcripts

def add_transcript(
    recording_id: str,
    text: str,
    language: str,
    provider: str,
    model: str,
    segments: list | None = None,
) -> str:
    res = db.transcripts.insert_one(
        {
            "recording_id": ObjectId(recording_id),
            "text": text,
            "language": language,
            "provider": provider,
            "model": model,
            "segments": segments or [],
            "created_at": datetime.utcnow(),
        }
    )
    return str(res.inserted_id)


# Evaluations

def add_evaluation(
    transcript_id: str,
    overall_level: str,
    confidence: float,
    scores: dict,
    rationale: str,
    tips: list[str] | None = None,
) -> str:
    res = db.evaluations.insert_one(
        {
            "transcript_id": ObjectId(transcript_id),
            "overall_level": overall_level,
            "confidence": confidence,
            "scores": scores,
            "rationale": rationale,
            "tips": tips or [],
            "created_at": datetime.utcnow(),
        }
    )
    return str(res.inserted_id)


# Queries

def list_sessions(user_id: str | None = None, limit: int = 20) -> list[dict]:
    q = {"user_id": ObjectId(user_id)} if user_id else {}
    return list(db.sessions.find(q).sort("started_at", -1).limit(limit))


def get_session_detail(session_id: str) -> dict:
    sid = ObjectId(session_id)
    s = db.sessions.find_one({"_id": sid})
    recs = list(db.recordings.find({"session_id": sid}).sort("created_at", -1))
    return {"session": s, "recordings": recs}
