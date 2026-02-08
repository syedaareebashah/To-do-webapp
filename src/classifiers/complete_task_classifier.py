"""
COMPLETE_TASK Intent Classifier for Todo AI Chatbot Agent

This module specifically handles classification of COMPLETE_TASK intents.
"""

from typing import Dict, Any
from ..models.intent import Intent, IntentType
from ..utils.confidence_scorer import get_confidence_score


class CompleteTaskClassifier:
    """
    Specialized classifier for COMPLETE_TASK intents.
    """

    def __init__(self):
        """
        Initialize the COMPLETE_TASK classifier.
        """
        self.keywords = [
            'complete', 'finish', 'done', 'mark as done', 'check', 'complete task',
            'finish task', 'done with', 'accomplish', 'achieve', 'execute',
            'carry out', 'perform', 'tick off', 'cross off'
        ]

        self.task_identifiers = [
            'task', 'number', '#', 'no.', 'item', 'todo', 'to-do'
        ]

    def classify(self, user_input: str) -> Intent:
        """
        Classify whether the input represents a COMPLETE_TASK intent.

        Args:
            user_input (str): The user's input string

        Returns:
            Intent: An Intent object with COMPLETE_TASK type and confidence score
        """
        confidence = self._calculate_complete_task_confidence(user_input)

        # Extract parameters for completing tasks
        parameters = self._extract_complete_task_parameters(user_input)

        intent = Intent(
            intent_type=IntentType.COMPLETE_TASK,
            confidence=confidence,
            parameters=parameters
        )

        return intent

    def _calculate_complete_task_confidence(self, user_input: str) -> float:
        """
        Calculate the confidence that the input represents a COMPLETE_TASK intent.

        Args:
            user_input (str): The user's input string

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        # Use the general confidence scorer as a baseline
        baseline_confidence = get_confidence_score(user_input, 'complete_task')

        input_lower = user_input.lower()

        # Check for presence of keywords
        keyword_matches = sum(1 for keyword in self.keywords if keyword in input_lower)

        # Boost confidence based on number of matches
        if keyword_matches >= 2:
            baseline_confidence = min(baseline_confidence + 0.25, 1.0)
        elif keyword_matches >= 1:
            baseline_confidence = min(baseline_confidence + 0.15, 1.0)

        # Boost confidence if we find strong indicators
        strong_indicators = ['complete', 'finish', 'done', 'mark as done', 'check']
        if any(indicator in input_lower for indicator in strong_indicators):
            baseline_confidence = min(baseline_confidence + 0.15, 1.0)

        # Boost confidence if we find task identifiers
        if any(tid in input_lower for tid in self.task_identifiers):
            baseline_confidence = min(baseline_confidence + 0.1, 1.0)

        # Reduce confidence if the input seems to be requesting a different action
        # like adding, listing, or deleting
        other_action_indicators = ['add', 'create', 'show', 'list', 'delete', 'remove', 'update', 'change']
        if any(indicator in input_lower for indicator in other_action_indicators):
            baseline_confidence = max(baseline_confidence - 0.2, 0.0)

        # Reduce confidence if the input seems more like a statement than a command
        if input_lower.startswith(('i', 'the', 'a', 'an')) and not any(indicator in input_lower for indicator in strong_indicators):
            baseline_confidence = max(baseline_confidence - 0.1, 0.0)

        return baseline_confidence

    def _extract_complete_task_parameters(self, user_input: str) -> Dict[str, Any]:
        """
        Extract parameters specific to COMPLETE_TASK intent.

        Args:
            user_input (str): The original user input

        Returns:
            Dict[str, Any]: Extracted parameters for complete task
        """
        import re

        parameters = {}

        # Extract task ID from the input
        # Look for patterns like "complete task 1", "finish task #2", etc.
        patterns = [
            r'(?:complete|finish|done|mark as done|check)\s+(?:task|number|#|no\.)\s*(\d+)',
            r'(?:task|number|#|no\.)\s*(\d+)\s+(?:is|has been|was)\s*(?:complete|finished|done)',
            r'(?:complete|finish|done|mark as done|check)\s*(\d+)',
        ]

        task_id = None
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                task_id = f"task_{match.group(1)}"
                break

        # If no specific task ID found in the patterns, try to extract numbers
        if not task_id:
            # Look for numbers in the input
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                # Use the first number as the task ID
                task_id = f"task_{numbers[0]}"

        if task_id:
            parameters['task_id'] = task_id

        # If no task ID could be extracted, mark as ambiguous
        if 'task_id' not in parameters:
            parameters['task_id'] = None
            parameters['error'] = 'Unable to identify task ID from input'

        return parameters

    def is_complete_task_intent(self, user_input: str, threshold: float = 0.5) -> bool:
        """
        Check if the input represents a COMPLETE_TASK intent with sufficient confidence.

        Args:
            user_input (str): The user's input string
            threshold (float): Confidence threshold for classification

        Returns:
            bool: True if the input is classified as COMPLETE_TASK with sufficient confidence
        """
        intent = self.classify(user_input)
        return intent.confidence >= threshold and 'task_id' in intent.parameters and intent.parameters['task_id'] is not None

    def can_extract_task_id(self, user_input: str) -> bool:
        """
        Check if a task ID can be extracted from the user input.

        Args:
            user_input (str): The user's input string

        Returns:
            bool: True if a task ID can be extracted, False otherwise
        """
        parameters = self._extract_complete_task_parameters(user_input)
        return 'task_id' in parameters and parameters['task_id'] is not None