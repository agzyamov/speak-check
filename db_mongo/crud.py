from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from .client import db
from .models import User, UserSession, PasswordResetToken, USER_COLLECTION, USER_SESSION_COLLECTION, PASSWORD_RESET_COLLECTION

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


# User Management

def create_user(user: User) -> str:
    """
    Create a new user in the database.
    
    Args:
        user: User object to create
        
    Returns:
        String ID of created user
    """
    user_dict = user.to_dict()
    if user_dict.get("_id") is None:
        user_dict.pop("_id", None)  # Remove None _id to let MongoDB generate it
    
    result = db[USER_COLLECTION].insert_one(user_dict)
    return str(result.inserted_id)


def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get user by ID.
    
    Args:
        user_id: User ID to search for
        
    Returns:
        User object if found, None otherwise
    """
    doc = db[USER_COLLECTION].find_one({"_id": ObjectId(user_id)})
    return User.from_dict(doc) if doc else None


def get_user_by_email(email: str) -> Optional[User]:
    """
    Get user by email address.
    
    Args:
        email: Email address to search for
        
    Returns:
        User object if found, None otherwise
    """
    doc = db[USER_COLLECTION].find_one({"email": email.lower().strip()})
    return User.from_dict(doc) if doc else None


def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update user data.
    
    Args:
        user_id: ID of user to update
        update_data: Dictionary of fields to update
        
    Returns:
        True if update was successful, False otherwise
    """
    # Add updated timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    result = db[USER_COLLECTION].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    return result.modified_count > 0


def update_user_last_login(user_id: str) -> bool:
    """
    Update user's last login timestamp.
    
    Args:
        user_id: ID of user to update
        
    Returns:
        True if update was successful, False otherwise
    """
    return update_user(user_id, {"last_login": datetime.utcnow()})


def deactivate_user(user_id: str) -> bool:
    """
    Deactivate user account (soft delete).
    
    Args:
        user_id: ID of user to deactivate
        
    Returns:
        True if deactivation was successful, False otherwise
    """
    return update_user(user_id, {"is_active": False})


def list_users(limit: int = 50, skip: int = 0, active_only: bool = True) -> List[User]:
    """
    List users with pagination.
    
    Args:
        limit: Maximum number of users to return
        skip: Number of users to skip
        active_only: Whether to return only active users
        
    Returns:
        List of User objects
    """
    query = {"is_active": True} if active_only else {}
    
    cursor = db[USER_COLLECTION].find(query).sort("created_at", -1).skip(skip).limit(limit)
    return [User.from_dict(doc) for doc in cursor]


# User Session Management

def create_user_session(session: UserSession) -> str:
    """
    Create a new user session.
    
    Args:
        session: UserSession object to create
        
    Returns:
        String ID of created session
    """
    result = db[USER_SESSION_COLLECTION].insert_one(session.to_dict())
    return str(result.inserted_id)


def get_user_session_by_token(token: str) -> Optional[UserSession]:
    """
    Get user session by token.
    
    Args:
        token: Session token to search for
        
    Returns:
        UserSession object if found and valid, None otherwise
    """
    now = datetime.utcnow()
    doc = db[USER_SESSION_COLLECTION].find_one({
        "token": token,
        "is_active": True,
        "expires_at": {"$gt": now}
    })
    return UserSession.from_dict(doc) if doc else None


def get_user_sessions(user_id: str, active_only: bool = True) -> List[UserSession]:
    """
    Get all sessions for a user.
    
    Args:
        user_id: User ID to get sessions for
        active_only: Whether to return only active sessions
        
    Returns:
        List of UserSession objects
    """
    query: Dict[str, Any] = {"user_id": ObjectId(user_id)}
    if active_only:
        query["is_active"] = True
        query["expires_at"] = {"$gt": datetime.utcnow()}
    
    cursor = db[USER_SESSION_COLLECTION].find(query).sort("created_at", -1)
    return [UserSession.from_dict(doc) for doc in cursor]


def invalidate_user_session(token: str) -> bool:
    """
    Invalidate a user session.
    
    Args:
        token: Session token to invalidate
        
    Returns:
        True if invalidation was successful, False otherwise
    """
    result = db[USER_SESSION_COLLECTION].update_one(
        {"token": token},
        {"$set": {"is_active": False}}
    )
    return result.modified_count > 0


def invalidate_user_sessions(user_id: str) -> int:
    """
    Invalidate all sessions for a user.
    
    Args:
        user_id: User ID to invalidate sessions for
        
    Returns:
        Number of sessions invalidated
    """
    result = db[USER_SESSION_COLLECTION].update_many(
        {"user_id": ObjectId(user_id)},
        {"$set": {"is_active": False}}
    )
    return result.modified_count


def cleanup_expired_sessions() -> int:
    """
    Clean up expired sessions from the database.
    
    Returns:
        Number of sessions cleaned up
    """
    now = datetime.utcnow()
    result = db[USER_SESSION_COLLECTION].delete_many({
        "$or": [
            {"expires_at": {"$lt": now}},
            {"is_active": False}
        ]
    })
    return result.deleted_count


# Password Reset Token Management

def create_password_reset_token(token: PasswordResetToken) -> str:
    """
    Create a password reset token.
    
    Args:
        token: PasswordResetToken object to create
        
    Returns:
        String ID of created token
    """
    result = db[PASSWORD_RESET_COLLECTION].insert_one(token.to_dict())
    return str(result.inserted_id)


def get_password_reset_token(token: str) -> Optional[PasswordResetToken]:
    """
    Get password reset token.
    
    Args:
        token: Reset token to search for
        
    Returns:
        PasswordResetToken object if found and valid, None otherwise
    """
    now = datetime.utcnow()
    doc = db[PASSWORD_RESET_COLLECTION].find_one({
        "token": token,
        "used": False,
        "expires_at": {"$gt": now}
    })
    return PasswordResetToken.from_dict(doc) if doc else None


def use_password_reset_token(token: str) -> bool:
    """
    Mark a password reset token as used.
    
    Args:
        token: Reset token to mark as used
        
    Returns:
        True if token was marked as used, False otherwise
    """
    result = db[PASSWORD_RESET_COLLECTION].update_one(
        {"token": token},
        {"$set": {"used": True}}
    )
    return result.modified_count > 0


def cleanup_expired_reset_tokens() -> int:
    """
    Clean up expired password reset tokens.
    
    Returns:
        Number of tokens cleaned up
    """
    now = datetime.utcnow()
    result = db[PASSWORD_RESET_COLLECTION].delete_many({
        "$or": [
            {"expires_at": {"$lt": now}},
            {"used": True}
        ]
    })
    return result.deleted_count


# Database Maintenance

def create_database_indexes() -> None:
    """Create database indexes for optimal performance."""
    from .models import DATABASE_INDEXES
    
    for collection_name, indexes in DATABASE_INDEXES.items():
        collection = db[collection_name]
        for index_spec in indexes:
            try:
                collection.create_index(list(index_spec.items()))
            except Exception as e:
                print(f"Warning: Could not create index {index_spec} on {collection_name}: {e}")
    
    # Create unique indexes
    try:
        db[USER_COLLECTION].create_index("email", unique=True)
        db[USER_SESSION_COLLECTION].create_index("token", unique=True)
        db[PASSWORD_RESET_COLLECTION].create_index("token", unique=True)
    except Exception as e:
        print(f"Warning: Could not create unique indexes: {e}")


def get_user_count() -> int:
    """Get total number of active users."""
    return db[USER_COLLECTION].count_documents({"is_active": True})


def get_session_count() -> int:
    """Get total number of active sessions."""
    now = datetime.utcnow()
    return db[USER_SESSION_COLLECTION].count_documents({
        "is_active": True,
        "expires_at": {"$gt": now}
    })
