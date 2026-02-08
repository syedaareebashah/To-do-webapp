"""
DELETE_TASK Intent Classifier for Todo AI Chatbot Agent

This module specifically handles classification of DELETE_TASK intents.
"""

from typing import Dict, Any
from ..models.intent import Intent, IntentType
from ..utils.confidence_scorer import get_confidence_score


class DeleteTaskClassifier:
    """
    Specialized classifier for DELETE_TASK intents.
    """

    def __init__(self):
        """
        Initialize the DELETE_TASK classifier.
        """
        self.keywords = [
            'delete', 'remove', 'cancel', 'erase', 'eliminate', 'get rid of',
            'dispose of', 'throw away', 'scrub', 'wipe', 'clear', 'purge',
            'delete task', 'remove task', 'cancel task'
        ]

        self.task_identifiers = [
            'task', 'number', '#', 'no.', 'item', 'todo', 'to-do'
        ]

    def classify(self, user_input: str) -> Intent:
        """
        Classify whether the input represents a DELETE_TASK intent.

        Args:
            user_input (str): The user's input string

        Returns:
            Intent: An Intent object with DELETE_TASK type and confidence score
        """
        confidence = self._calculate_delete_task_confidence(user_input)

        # Extract parameters for deleting tasks
        parameters = self._extract_delete_task_parameters(user_input)

        intent = Intent(
            intent_type=IntentType.DELETE_TASK,
            confidence=confidence,
            parameters=parameters
        )

        return intent

    def _calculate_delete_task_confidence(self, user_input: str) -> float:
        """
        Calculate the confidence that the input represents a DELETE_TASK intent.

        Args:
            user_input (str): The user's input string

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        # Use the general confidence scorer as a baseline
        baseline_confidence = get_confidence_score(user_input, 'delete_task')

        input_lower = user_input.lower()

        # Check for presence of keywords
        keyword_matches = sum(1 for keyword in self.keywords if keyword in input_lower)

        # Boost confidence based on number of matches
        if keyword_matches >= 2:
            baseline_confidence = min(baseline_confidence + 0.25, 1.0)
        elif keyword_matches >= 1:
            baseline_confidence = min(baseline_confidence + 0.15, 1.0)

        # Boost confidence if we find strong indicators
        strong_indicators = ['delete', 'remove', 'cancel']
        if any(indicator in input_lower for indicator in strong_indicators):
            baseline_confidence = min(baseline_confidence + 0.2, 1.0)

        # Boost confidence if we find task identifiers
        if any(tid in input_lower for tid in self.task_identifiers):
            baseline_confidence = min(baseline_confidence + 0.1, 1.0)

        # Reduce confidence if the input seems to be requesting a different action
        # like adding, listing, or completing
        other_action_indicators = ['add', 'create', 'show', 'list', 'complete', 'finish', 'update', 'change']
        if any(indicator in input_lower for indicator in other_action_indicators):
            baseline_confidence = max(baseline_confidence - 0.2, 0.0)

        # Reduce confidence if the input seems too vague or general
        if len(user_input.split()) < 2:
            baseline_confidence = max(baseline_confidence - 0.15, 0.0)

        return baseline_confidence

    def _extract_delete_task_parameters(self, user_input: str) -> Dict[str, Any]:
        """
        Extract parameters specific to DELETE_TASK intent.

        Args:
            user_input (str): The original user input

        Returns:
            Dict[str, Any]: Extracted parameters for delete task
        """
        import re

        parameters = {}

        # Extract task ID from the input
        # Look for patterns like "delete task 1", "remove task #2", etc.
        patterns = [
            r'(?:delete|remove|cancel|erase|eliminate)\s+(?:task|number|#|no\.)\s*(\d+)',
            r'(?:task|number|#|no\.)\s*(\d+)\s+(?:is|has been|was)\s*(?:deleted|removed|cancelled)',
            r'(?:delete|remove|cancel)\s*(\d+)',
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

    def is_delete_task_intent(self, user_input: str, threshold: float = 0.5) -> bool:
        """
        Check if the input represents a DELETE_TASK intent with sufficient confidence.

        Args:
            user_input (str): The user's input string
            threshold (float): Confidence threshold for classification

        Returns:
            bool: True if the input is classified as DELETE_TASK with sufficient confidence
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
        parameters = self._extract_delete_task_parameters(user_input)
        return 'task_id' in parameters and parameters['task_id'] is not None