"""
OpenAI-based CEFR Assessment Module

This module provides AI-powered evaluation of speaking responses using OpenAI's GPT models
to assess CEFR levels and provide detailed feedback.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CEFRAssessment:
    """Structured CEFR assessment result."""
    overall_level: str  # A2, B1, B2, C1
    confidence: float  # 0.0-1.0
    scores: Dict[str, float]  # fluency, accuracy, grammar, vocabulary, coherence
    word_count: int
    rationale: str
    actionable_tips: List[str]
    strengths: List[str]
    areas_for_improvement: List[str]

def _ensure_openai_available() -> bool:
    """Check if OpenAI client is available and API key is set."""
    try:
        from openai import OpenAI  # noqa: F401
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            return False
        return True
    except Exception:
        logger.error("OpenAI client not installed. Run: pip install openai")
        return False

def _create_assessment_prompt(transcript: str, target_level: str, question: str) -> str:
    """Create a structured prompt for CEFR assessment."""
    
    # Truncate very long transcripts to avoid token limits
    max_words = 300
    words = transcript.split()
    if len(words) > max_words:
        transcript = " ".join(words[:max_words]) + " [truncated]"
    
    prompt = f"""You are an expert CEFR (Common European Framework of Reference) assessor. 
Evaluate the following English speaking response and provide a structured assessment.

QUESTION: {question}
TARGET LEVEL: {target_level}
RESPONSE: "{transcript}"

Provide your assessment in the following JSON format:
{{
    "overall_level": "A2|B1|B2|C1",
    "confidence": 0.0-1.0,
    "scores": {{
        "fluency": 0.0-10.0,
        "accuracy": 0.0-10.0, 
        "grammar": 0.0-10.0,
        "vocabulary": 0.0-10.0,
        "coherence": 0.0-10.0
    }},
    "word_count": <integer>,
    "rationale": "<detailed explanation of the assessment>",
    "actionable_tips": ["<specific tip 1>", "<specific tip 2>", ...],
    "strengths": ["<strength 1>", "<strength 2>", ...],
    "areas_for_improvement": ["<area 1>", "<area 2>", ...]
}}

Assessment criteria:
- Fluency: Natural flow, hesitations, speech rate
- Accuracy: Grammatical correctness, vocabulary precision  
- Grammar: Sentence structure complexity, error patterns
- Vocabulary: Word choice, lexical range, sophistication
- Coherence: Logical organization, topic relevance, completeness

CEFR level guidelines:
- A2: Basic phrases, simple sentences, familiar topics (50+ words)
- B1: Connected speech, personal experiences, some complexity (100+ words)  
- B2: Spontaneous interaction, abstract topics, detailed explanations (150+ words)
- C1: Flexible language use, complex arguments, subtle meanings (200+ words)

Respond only with valid JSON."""

    return prompt

def assess_speaking_response(
    transcript: str,
    target_level: str = "B1", 
    question: str = "",
    model: str = "gpt-4o-mini"
) -> CEFRAssessment:
    """
    Assess a speaking response using OpenAI GPT for CEFR evaluation.
    
    Args:
        transcript: The transcribed speech text
        target_level: Target CEFR level (A2, B1, B2, C1)
        question: The original speaking prompt/question
        model: OpenAI model to use for assessment
        
    Returns:
        CEFRAssessment: Structured assessment results
    """
    if not _ensure_openai_available():
        return _fallback_assessment(transcript, target_level)
    
    if not transcript or not transcript.strip():
        return _fallback_assessment("", target_level)
    
    try:
        from openai import OpenAI
        
        client = OpenAI()
        prompt = _create_assessment_prompt(transcript, target_level, question)
        
        logger.info(f"Assessing transcript with OpenAI {model}")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert CEFR assessor. Provide assessments in valid JSON format only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1,  # Low temperature for consistent assessments
            max_tokens=1000
        )
        
        # Parse the JSON response
        try:
            result_data = json.loads(response.choices[0].message.content)
            
            return CEFRAssessment(
                overall_level=result_data.get("overall_level", "B1"),
                confidence=float(result_data.get("confidence", 0.7)),
                scores=result_data.get("scores", {
                    "fluency": 6.0, "accuracy": 6.0, "grammar": 6.0, 
                    "vocabulary": 6.0, "coherence": 6.0
                }),
                word_count=int(result_data.get("word_count", len(transcript.split()))),
                rationale=result_data.get("rationale", "Assessment completed"),
                actionable_tips=result_data.get("actionable_tips", []),
                strengths=result_data.get("strengths", []),
                areas_for_improvement=result_data.get("areas_for_improvement", [])
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            return _fallback_assessment(transcript, target_level)
            
    except Exception as e:
        logger.error(f"OpenAI assessment error: {e}")
        return _fallback_assessment(transcript, target_level)

def _fallback_assessment(transcript: str, target_level: str) -> CEFRAssessment:
    """Provide a basic fallback assessment when OpenAI is unavailable."""
    
    word_count = len(transcript.split()) if transcript else 0
    
    # Simple heuristics for fallback
    if word_count < 30:
        level = "A2"
        scores = {"fluency": 4.0, "accuracy": 4.0, "grammar": 4.0, "vocabulary": 4.0, "coherence": 4.0}
    elif word_count < 80:
        level = "B1" 
        scores = {"fluency": 6.0, "accuracy": 6.0, "grammar": 6.0, "vocabulary": 6.0, "coherence": 6.0}
    elif word_count < 150:
        level = "B2"
        scores = {"fluency": 7.0, "accuracy": 7.0, "grammar": 7.0, "vocabulary": 7.0, "coherence": 7.0}
    else:
        level = "C1"
        scores = {"fluency": 8.0, "accuracy": 8.0, "grammar": 8.0, "vocabulary": 8.0, "coherence": 8.0}
    
    return CEFRAssessment(
        overall_level=level,
        confidence=0.5,
        scores=scores,
        word_count=word_count,
        rationale="Basic assessment using word count and simple heuristics",
        actionable_tips=["Practice speaking more to improve fluency", "Expand vocabulary"],
        strengths=["Good effort in responding"],
        areas_for_improvement=["Consider using more complex structures", "Work on accuracy"]
    )

def is_available() -> bool:
    """Check if OpenAI assessment is available."""
    return _ensure_openai_available()

def get_assessment_providers() -> List[str]:
    """Get available assessment providers."""
    providers = ["baseline"]
    if is_available():
        providers.append("openai")
    return providers
