"""
User feedback API endpoints.
Allows users to provide feedback on recommendations and system performance.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
import os

router = APIRouter()


class FeedbackSubmission(BaseModel):
    """User feedback submission model."""
    feedback_type: str  # 'recommendation', 'forecast', 'general', 'bug'
    rating: Optional[int] = None  # 1-5 stars
    crop: Optional[str] = None
    location_name: Optional[str] = None
    comment: Optional[str] = None
    was_helpful: Optional[bool] = None
    actual_outcome: Optional[str] = None  # What actually happened
    user_email: Optional[str] = None  # Optional for follow-up


class FeedbackResponse(BaseModel):
    """Feedback submission response."""
    success: bool
    message: str
    feedback_id: str


# In-memory feedback storage (in production, use database)
feedback_storage = []


@router.post("/feedback/submit", response_model=FeedbackResponse)
def submit_feedback(feedback: FeedbackSubmission):
    """Submit user feedback."""
    try:
        # Generate feedback ID
        feedback_id = f"FB{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create feedback record
        feedback_record = {
            "id": feedback_id,
            "timestamp": datetime.now().isoformat(),
            "type": feedback.feedback_type,
            "rating": feedback.rating,
            "crop": feedback.crop,
            "location": feedback.location_name,
            "comment": feedback.comment,
            "was_helpful": feedback.was_helpful,
            "actual_outcome": feedback.actual_outcome,
            "user_email": feedback.user_email
        }
        
        # Store feedback
        feedback_storage.append(feedback_record)
        
        # In production, save to database or file
        _save_feedback_to_file(feedback_record)
        
        return FeedbackResponse(
            success=True,
            message="Thank you for your feedback! It helps us improve GramSense AI.",
            feedback_id=feedback_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/feedback/stats")
def get_feedback_stats():
    """Get feedback statistics (admin endpoint)."""
    if not feedback_storage:
        return {
            "total_feedback": 0,
            "average_rating": 0,
            "helpful_percentage": 0,
            "feedback_by_type": {}
        }
    
    total = len(feedback_storage)
    ratings = [f["rating"] for f in feedback_storage if f["rating"] is not None]
    helpful = [f for f in feedback_storage if f.get("was_helpful") is True]
    
    # Count by type
    type_counts = {}
    for f in feedback_storage:
        ftype = f["type"]
        type_counts[ftype] = type_counts.get(ftype, 0) + 1
    
    return {
        "total_feedback": total,
        "average_rating": sum(ratings) / len(ratings) if ratings else 0,
        "helpful_percentage": (len(helpful) / total * 100) if total > 0 else 0,
        "feedback_by_type": type_counts,
        "recent_feedback": feedback_storage[-5:]  # Last 5 feedback items
    }


@router.get("/feedback/recent")
def get_recent_feedback(limit: int = 10):
    """Get recent feedback submissions (admin endpoint)."""
    return {
        "count": len(feedback_storage),
        "feedback": feedback_storage[-limit:]
    }


def _save_feedback_to_file(feedback_record: dict):
    """Save feedback to JSON file for persistence."""
    try:
        feedback_file = "feedback_data.json"
        
        # Load existing feedback
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r') as f:
                all_feedback = json.load(f)
        else:
            all_feedback = []
        
        # Append new feedback
        all_feedback.append(feedback_record)
        
        # Save back to file
        with open(feedback_file, 'w') as f:
            json.dump(all_feedback, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save feedback to file: {e}")


# Feedback prompts for different scenarios
FEEDBACK_PROMPTS = {
    "after_recommendation": {
        "title": "How helpful was this recommendation?",
        "questions": [
            "Did you follow this recommendation?",
            "What was the actual outcome?",
            "How would you rate this advice? (1-5 stars)"
        ]
    },
    "after_forecast": {
        "title": "Was this forecast accurate?",
        "questions": [
            "How close was the forecast to actual prices?",
            "Did this help your decision-making?",
            "Rate the forecast accuracy (1-5 stars)"
        ]
    },
    "general": {
        "title": "Help us improve GramSense AI",
        "questions": [
            "What features would you like to see?",
            "What can we improve?",
            "Overall experience rating (1-5 stars)"
        ]
    }
}


@router.get("/feedback/prompts")
def get_feedback_prompts():
    """Get feedback prompts for different scenarios."""
    return FEEDBACK_PROMPTS
