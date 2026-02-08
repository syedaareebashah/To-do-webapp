"""
Confidence Scoring Utility for Todo AI Chatbot Agent

This module provides utilities for calculating and managing confidence scores
for intent classification.
"""

from typing import Dict, Any, List, Optional
import re


class ConfidenceScorer:
    """
    Utility class for calculating and managing confidence scores.
    """

    def __init__(self):
        """
        Initialize the confidence scorer with default parameters.
        """
        # Define keyword weights for different intents
        self.keyword_weights = {
            'add_task': {
                'add': 0.9,
                'create': 0.9,
                'make': 0.8,
                'remember': 0.8,
                'schedule': 0.8,
                'new': 0.7,
                'task': 0.5,
                'todo': 0.5
            },
            'list_tasks': {
                'show': 0.9,
                'list': 0.9,
                'view': 0.8,
                'display': 0.8,
                'see': 0.8,
                'get': 0.7,
                'my': 0.5,
                'tasks': 0.8,
                'todos': 0.8
            },
            'complete_task': {
                'complete': 0.9,
                'finish': 0.9,
                'done': 0.9,
                'mark': 0.7,
                'as': 0.5,
                'check': 0.7
            },
            'delete_task': {
                'delete': 0.95,
                'remove': 0.9,
                'cancel': 0.85,
                'erase': 0.8,
                'eliminate': 0.8
            },
            'update_task': {
                'update': 0.9,
                'change': 0.9,
                'modify': 0.9,
                'edit': 0.9,
                'adjust': 0.8
            }
        }

    def calculate_confidence(self, user_input: str, intent_type: str) -> float:
        """
        Calculate confidence score for a specific intent type based on user input.

        Args:
            user_input (str): The user's input text
            intent_type (str): The intent type to calculate confidence for

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        if intent_type not in self.keyword_weights:
            return 0.0

        # Normalize input: convert to lowercase and remove punctuation
        normalized_input = re.sub(r'[^\w\s]', ' ', user_input.lower())
        input_words = set(normalized_input.split())

        # Get weights for this intent type
        weights = self.keyword_weights[intent_type]

        # Calculate weighted score
        total_weight = 0.0
        max_possible_weight = 0.0

        for word in input_words:
            if word in weights:
                total_weight += weights[word]

            # Add to max possible weight for each word in weights
            max_possible_weight += weights.get(word, 0)

        # If no keywords matched, return a base confidence
        if max_possible_weight == 0:
            return self._calculate_base_confidence(user_input, intent_type)

        # Calculate confidence as ratio of matched weight to possible weight
        confidence = min(total_weight / max_possible_weight, 1.0)

        # Apply additional factors based on input characteristics
        confidence = self._apply_contextual_factors(confidence, user_input, intent_type)

        return confidence

    def _calculate_base_confidence(self, user_input: str, intent_type: str) -> float:
        """
        Calculate a base confidence when no keywords match.

        Args:
            user_input (str): The user's input text
            intent_type (str): The intent type

        Returns:
            float: Base confidence score
        """
        # If no keywords match, assign a very low confidence
        # unless the input somehow still seems to match the intent pattern
        input_lower = user_input.lower()

        # Check for partial matches or patterns
        if intent_type == 'add_task' and any(p in input_lower for p in ['want to', 'need to', 'should']):
            return 0.2
        elif intent_type == 'list_tasks' and any(p in input_lower for p in ['what', 'which', 'how many']):
            return 0.2
        elif intent_type in ['complete_task', 'delete_task'] and 'task' in input_lower:
            return 0.15

        return 0.05  # Very low confidence if nothing matches

    def _apply_contextual_factors(self, base_confidence: float, user_input: str, intent_type: str) -> float:
        """
        Apply additional factors that affect confidence based on context.

        Args:
            base_confidence (float): Base confidence score
            user_input (str): The user's input text
            intent_type (str): The intent type

        Returns:
            float: Adjusted confidence score
        """
        adjusted_confidence = base_confidence

        # Boost confidence if there are strong indicator words
        strong_indicators = {
            'add_task': ['please add', 'can you create', 'i need to add'],
            'list_tasks': ['show me', 'list all', 'what are my', 'display'],
            'complete_task': ['please complete', 'mark as done', 'finish task'],
            'delete_task': ['please delete', 'remove task', 'get rid of'],
            'update_task': ['update task', 'change task', 'modify task']
        }

        input_lower = user_input.lower()
        if intent_type in strong_indicators:
            for indicator in strong_indicators[intent_type]:
                if indicator in input_lower:
                    adjusted_confidence = min(adjusted_confidence * 1.3, 1.0)
                    break

        # Reduce confidence if input is very short (might be ambiguous)
        if len(user_input.strip().split()) < 3 and adjusted_confidence > 0.5:
            adjusted_confidence *= 0.8

        return adjusted_confidence

    def calculate_multi_intent_confidence(self, user_input: str) -> Dict[str, float]:
        """
        Calculate confidence scores for all intent types.

        Args:
            user_input (str): The user's input text

        Returns:
            Dict[str, float]: Dictionary mapping intent types to their confidence scores
        """
        confidences = {}
        for intent_type in self.keyword_weights.keys():
            confidences[intent_type] = self.calculate_confidence(user_input, intent_type)

        return confidences

    def normalize_confidences(self, confidences: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize confidence scores so they sum to 1.0 (or close to it).

        Args:
            confidences (Dict[str, float]): Raw confidence scores

        Returns:
            Dict[str, float]: Normalized confidence scores
        """
        total = sum(confidences.values())

        if total == 0:
            return confidences

        return {k: v / total for k, v in confidences.items()}


# Global instance for easy access
confidence_scorer = ConfidenceScorer()


def get_confidence_score(user_input: str, intent_type: str) -> float:
    """
    Convenience function to get confidence score for a specific intent.

    Args:
        user_input (str): The user's input text
        intent_type (str): The intent type to calculate confidence for

    Returns:
        float: Confidence score between 0.0 and 1.0
    """
    return confidence_scorer.calculate_confidence(user_input, intent_type)


def get_all_confidences(user_input: str) -> Dict[str, float]:
    """
    Convenience function to get confidence scores for all intents.

    Args:
        user_input (str): The user's input text

    Returns:
        Dict[str, float]: Dictionary mapping intent types to their confidence scores
    """
    return confidence_scorer.calculate_multi_intent_confidence(user_input)