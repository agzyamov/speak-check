"""
CEFR Speaking Questions Module

This module contains speaking prompts and questions organized by CEFR levels (A2-C1).
Each level has different types of speaking tasks appropriate for that proficiency level.
"""

import random
from typing import Dict, List

# TODO: Expand question database with more varied prompts
# TODO: Add question categories (personal, academic, professional, etc.)
# TODO: Implement question difficulty scoring within levels
# TODO: Add multimedia prompts (images, scenarios)
# TODO: Store questions in external database or JSON file

def get_question_by_level(cefr_level: str) -> str:
    """
    Retrieve a random speaking question appropriate for the specified CEFR level.
    
    Args:
        cefr_level (str): The CEFR level (A2, B1, B2, C1)
        
    Returns:
        str: A speaking prompt/question for the specified level
    """
    questions = QUESTIONS_DB.get(cefr_level, [])
    
    if not questions:
        return f"No questions available for level {cefr_level}"
    
    return random.choice(questions)

def get_all_questions_by_level(cefr_level: str) -> List[str]:
    """
    Get all questions for a specific CEFR level.
    
    Args:
        cefr_level (str): The CEFR level (A2, B1, B2, C1)
        
    Returns:
        List[str]: List of all questions for the specified level
    """
    return QUESTIONS_DB.get(cefr_level, [])

def get_question_by_category(cefr_level: str, category: str) -> str:
    """
    Get a question from a specific category and CEFR level.
    
    Args:
        cefr_level (str): The CEFR level (A2, B1, B2, C1)
        category (str): Question category (personal, work, travel, etc.)
        
    Returns:
        str: A speaking prompt for the specified level and category
    """
    # TODO: Implement category-based question selection
    return get_question_by_level(cefr_level)

# Sample questions database organized by CEFR level
# TODO: Expand this with more comprehensive question sets
QUESTIONS_DB: Dict[str, List[str]] = {
    "A2": [
        "Tell me about your family. Who do you live with?",
        "Describe your daily routine. What time do you wake up?",
        "What is your favorite food? Why do you like it?",
        "Talk about your hometown. What is it like?",
        "Describe your best friend. What do you like to do together?",
        "What do you like to do in your free time?",
        "Talk about your last vacation. Where did you go?",
        "Describe your house or apartment. How many rooms does it have?"
    ],
    
    "B1": [
        "Describe a memorable experience from your childhood and explain why it was important to you.",
        "Talk about a skill you would like to learn and explain your reasons.",
        "Discuss the advantages and disadvantages of living in a big city versus a small town.",
        "Describe a book or movie that made a strong impression on you and explain why.",
        "Talk about environmental problems in your country and suggest possible solutions.",
        "Discuss how technology has changed the way people communicate.",
        "Describe a person who has influenced your life and explain how.",
        "Talk about your plans for the future and what you hope to achieve."
    ],
    
    "B2": [
        "Analyze the role of social media in modern society and discuss its impact on relationships.",
        "Compare the educational systems of different countries and evaluate their effectiveness.",
        "Discuss the challenges facing young people today and propose solutions.",
        "Evaluate the importance of work-life balance in today's fast-paced world.",
        "Analyze the impact of globalization on local cultures and traditions.",
        "Discuss the ethical implications of artificial intelligence in various sectors.",
        "Evaluate the role of government in addressing climate change.",
        "Analyze the changing nature of work and its implications for future generations."
    ],
    
    "C1": [
        "Critically evaluate the statement: 'Traditional universities will become obsolete within the next 20 years.'",
        "Analyze the complex relationship between economic development and environmental sustainability.",
        "Discuss the philosophical and practical implications of genetic engineering in human medicine.",
        "Evaluate the role of international organizations in addressing global conflicts and crises.",
        "Analyze the impact of demographic changes on social policy and economic planning.",
        "Critically assess the balance between individual privacy and collective security in the digital age.",
        "Examine the cultural and economic factors that drive migration patterns in the 21st century.",
        "Analyze the evolving definition of success in contemporary society and its psychological implications."
    ]
}

def get_question_metadata(cefr_level: str) -> Dict:
    """
    Get metadata about questions for a specific CEFR level.
    
    Args:
        cefr_level (str): The CEFR level (A2, B1, B2, C1)
        
    Returns:
        Dict: Metadata including count, topics, difficulty range
    """
    questions = QUESTIONS_DB.get(cefr_level, [])
    
    return {
        "level": cefr_level,
        "question_count": len(questions),
        "topics": _extract_topics(cefr_level),  # TODO: Implement topic extraction
        "average_length": sum(len(q) for q in questions) // len(questions) if questions else 0,
        "difficulty_range": _get_difficulty_range(cefr_level)  # TODO: Implement difficulty scoring
    }

def _extract_topics(cefr_level: str) -> List[str]:
    """Extract main topics from questions (placeholder implementation)."""
    # TODO: Implement actual topic extraction from question content
    topic_mapping = {
        "A2": ["family", "daily_routine", "food", "travel", "hobbies"],
        "B1": ["experiences", "skills", "city_life", "entertainment", "environment"],
        "B2": ["social_issues", "education", "technology", "work", "culture"],
        "C1": ["philosophy", "economics", "ethics", "politics", "society"]
    }
    return topic_mapping.get(cefr_level, [])

def _get_difficulty_range(cefr_level: str) -> Dict[str, int]:
    """Get difficulty range for a CEFR level (placeholder implementation)."""
    # TODO: Implement actual difficulty scoring based on linguistic complexity
    difficulty_mapping = {
        "A2": {"min": 1, "max": 3},
        "B1": {"min": 3, "max": 5},
        "B2": {"min": 5, "max": 7},
        "C1": {"min": 7, "max": 10}
    }
    return difficulty_mapping.get(cefr_level, {"min": 1, "max": 10})