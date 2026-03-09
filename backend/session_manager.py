"""
Session manager for conversation history.

Manages user sessions and conversation history with automatic cleanup.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import time


class Message(BaseModel):
    """Represents a single message in conversation history."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    crop: Optional[str] = None
    location: Optional[str] = None


class Session(BaseModel):
    """Represents a user session with conversation history."""
    session_id: str
    created_at: datetime
    last_activity: datetime
    messages: List[Message] = []
    
    def add_message(self, role: str, content: str, crop: Optional[str] = None, location: Optional[str] = None):
        """Add a message to the conversation history."""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            crop=crop,
            location=location
        )
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get the most recent messages."""
        return self.messages[-limit:]
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired."""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)


class SessionManager:
    """Manages user sessions and conversation history."""
    
    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initialize session manager.
        
        Args:
            session_timeout_minutes: Minutes of inactivity before session expires
        """
        self.sessions: Dict[str, Session] = {}
        self.session_timeout_minutes = session_timeout_minutes
        self._last_cleanup = time.time()
    
    def create_session(self) -> str:
        """Create a new session and return session ID."""
        session_id = str(uuid.uuid4())
        session = Session(
            session_id=session_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            messages=[]
        )
        self.sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        session = self.sessions.get(session_id)
        
        if session and session.is_expired(self.session_timeout_minutes):
            # Remove expired session
            del self.sessions[session_id]
            return None
        
        return session
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, Session]:
        """Get existing session or create new one."""
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session_id, session
        
        # Create new session
        new_session_id = self.create_session()
        return new_session_id, self.sessions[new_session_id]
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        crop: Optional[str] = None,
        location: Optional[str] = None
    ):
        """Add a message to a session."""
        session = self.get_session(session_id)
        if session:
            session.add_message(role, content, crop, location)
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Message]:
        """Get conversation history for a session."""
        session = self.get_session(session_id)
        if session:
            return session.get_recent_messages(limit)
        return []
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        current_time = time.time()
        
        # Cleanup every 5 minutes
        if current_time - self._last_cleanup < 300:
            return
        
        self._last_cleanup = current_time
        
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(self.session_timeout_minutes)
        ]
        
        for sid in expired_sessions:
            del self.sessions[sid]
    
    def get_stats(self) -> dict:
        """Get session manager statistics."""
        return {
            "active_sessions": len(self.sessions),
            "session_timeout_minutes": self.session_timeout_minutes,
            "total_messages": sum(len(s.messages) for s in self.sessions.values())
        }


# Global session manager instance
session_manager = SessionManager(session_timeout_minutes=30)
