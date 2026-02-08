"""
UPDATE_TASK Intent Classifier for Todo AI Chatbot Agent

This module specifically handles classification of UPDATE_TASK intents.
"""

from typing import Dict, Any
from ..models.intent import Intent, IntentType
from ..utils.confidence_scorer import get_confidence_score


class UpdateTaskClassifier:
    """
    Specialized classifier for UPDATE_TASK intents.
    """

    def __init__(self):
        """
        Initialize the UPDATE_TASK classifier.
        """
        self.keywords = [
            'update', 'change', 'modify', 'edit', 'adjust', 'alter', 'revise',
            'modify task', 'change task', 'update task', 'edit task', 'adjust task'
        ]

        self.task_identifiers = [
            'task', 'number', '#', 'no.', 'item', 'todo', 'to-do'
        ]

        self.update_types = {
            'content': ['content', 'text', 'description', 'detail', 'info', 'information'],
            'priority': ['priority', 'importance', 'urgency', 'level'],
            'status': ['status', 'state', 'completion', 'done'],
            'due_date': ['due date', 'date', 'deadline', 'time', 'when']
        }

    def classify(self, user_input: str) -> Intent:
        """
        Classify whether the input represents an UPDATE_TASK intent.

        Args:
            user_input (str): The user's input string

        Returns:
            Intent: An Intent object with UPDATE_TASK type and confidence score
        """
        confidence = self._calculate_update_task_confidence(user_input)

        # Extract parameters for updating tasks
        parameters = self._extract_update_task_parameters(user_input)

        intent = Intent(
            intent_type=IntentType.UPDATE_TASK,
            confidence=confidence,
            parameters=parameters
        )

        return intent

    def _calculate_update_task_confidence(self, user_input: str) -> float:
        """
        Calculate the confidence that the input represents an UPDATE_TASK intent.

        Args:
            user_input (str): The user's input string

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        # Use the general confidence scorer as a baseline
        baseline_confidence = get_confidence_score(user_input, 'update_task')

        input_lower = user_input.lower()

        # Check for presence of keywords
        keyword_matches = sum(1 for keyword in self.keywords if keyword in input_lower)

        # Boost confidence based on number of matches
        if keyword_matches >= 2:
            baseline_confidence = min(baseline_confidence + 0.25, 1.0)
        elif keyword_matches >= 1:
            baseline_confidence = min(baseline_confidence + 0.15, 1.0)

        # Boost confidence if we find strong indicators
        strong_indicators = ['update', 'change', 'modify', 'edit', 'adjust']
        if any(indicator in input_lower for indicator in strong_indicators):
            baseline_confidence = min(baseline_confidence + 0.2, 1.0)

        # Boost confidence if we find task identifiers
        if any(tid in input_lower for tid in self.task_identifiers):
            baseline_confidence = min(baseline_confidence + 0.1, 1.0)

        # Boost confidence if we find update indicators
        update_indicators = []
        for category, indicators in self.update_types.items():
            update_indicators.extend(indicators)

        if any(ui in input_lower for ui in update_indicators):
            baseline_confidence = min(baseline_confidence + 0.15, 1.0)

        # Reduce confidence if the input seems to be requesting a different action
        # like adding, listing, completing, or deleting
        other_action_indicators = ['add', 'create', 'show', 'list', 'complete', 'finish', 'delete', 'remove']
        if any(indicator in input_lower for indicator in other_action_indicators):
            baseline_confidence = max(baseline_confidence - 0.2, 0.0)

        # Reduce confidence if the input seems too vague or general
        if len(user_input.split()) < 3:
            baseline_confidence = max(baseline_confidence - 0.15, 0.0)

        return baseline_confidence

    def _extract_update_task_parameters(self, user_input: str) -> Dict[str, Any]:
        """
        Extract parameters specific to UPDATE_TASK intent.

        Args:
            user_input (str): The original user input

        Returns:
            Dict[str, Any]: Extracted parameters for update task
        """
        import re

        parameters = {'updates': {}}

        # Extract task ID from the input
        # Look for patterns like "update task 1", "change task #2", etc.
        patterns = [
            r'(?:update|change|modify|edit|adjust)\s+(?:task|number|#|no\.)\s*(\d+)',
            r'(?:task|number|#|no\.)\s*(\d+)\s+(?:is|has been|was)\s*(?:updated|changed|modified|edited|adjusted)',
        ]

        task_id = None
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                task_id = f"task_{match.group(1)}"
                break

        # If no specific task ID found in the patterns, try to extract numbers
        if not task_id:
            # Look for numbers in the input near task identifiers
            task_num_pattern = r'(?:task|number|#|no\.)\s*(\d+)'
            num_matches = re.findall(task_num_pattern, user_input, re.IGNORECASE)
            if num_matches:
                task_id = f"task_{num_matches[0]}"
            else:
                # Look for any numbers in the input
                numbers = re.findall(r'\d+', user_input)
                if numbers:
                    # Use the first number as the task ID
                    task_id = f"task_{numbers[0]}"

        if task_id:
            parameters['task_id'] = task_id

        # Extract what needs to be updated
        input_lower = user_input.lower()

        # Look for content updates
        content_patterns = [
            r'(?:change|update|modify|edit)\s+(?:content|text|description|detail|info|information)\s+to\s+(.+?)(?:\s+and|\s+with|\s+or|\s+that|$)',
            r'(?:update|change|modify|edit)\s+(?:the\s+)?(.+?)\s+of\s+task.*?(?:to|with)\s+(.+?)(?:\s+and|\s+with|\s+or|\s+that|$)',
        ]

        for pattern in content_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match and len(match.groups()) > 1:
                field = match.group(1).strip().lower()
                value = match.group(2).strip()

                # Check if the field matches known update types
                for update_type, indicators in self.update_types.items():
                    if any(indicator in field for indicator in indicators):
                        parameters['updates'][update_type] = value
                        break
                else:
                    # If it's a general update, treat it as content
                    parameters['updates']['content'] = value
            elif match:
                # If only one group, treat as content
                content_value = match.group(1).strip()
                parameters['updates']['content'] = content_value

        # Look for priority updates
        priority_pattern = r'(?:change|update|set)\s+(?:the\s+)?(?:priority|importance|urgency)\s+(?:to|as|at)\s+(high|medium|low)'
        priority_match = re.search(priority_pattern, user_input, re.IGNORECASE)
        if priority_match:
            parameters['updates']['priority'] = priority_match.group(1).lower()

        # Look for status updates
        status_pattern = r'(?:change|update|set)\s+(?:the\s+)?(?:status|state|completion)\s+(?:to|as|at)\s+(pending|completed|incomplete|done)'
        status_match = re.search(status_pattern, user_input, re.IGNORECASE)
        if status_match:
            parameters['updates']['status'] = status_match.group(1).lower()

        # Look for due date updates
        date_pattern = r'(?:change|update|set)\s+(?:the\s+)?(?:due\s+date|date|deadline)\s+(?:to|as|at)\s+(.+)'
        date_match = re.search(date_pattern, user_input, re.IGNORECASE)
        if date_match:
            parameters['updates']['due_date'] = date_match.group(1).strip()

        # If no specific updates found, try to extract from general phrasing
        if not parameters['updates']:
            # Look for general update phrases
            general_update_pattern = r'(?:update|change|modify|edit|adjust)\s+task.*?(?:to|with|as|into)\s+(.+)'
            general_match = re.search(general_update_pattern, user_input, re.IGNORECASE)
            if general_match:
                parameters['updates']['content'] = general_match.group(1).strip()

        # If no task ID could be extracted, mark as ambiguous
        if 'task_id' not in parameters:
            parameters['task_id'] = None
            parameters['error'] = 'Unable to identify task ID from input'

        # If no updates could be extracted, mark as ambiguous
        if not parameters['updates']:
            parameters['error'] = 'Unable to identify what to update in the input'

        return parameters

    def is_update_task_intent(self, user_input: str, threshold: float = 0.5) -> bool:
        """
        Check if the input represents an UPDATE_TASK intent with sufficient confidence.

        Args:
            user_input (str): The user's input string
            threshold (float): Confidence threshold for classification

        Returns:
            bool: True if the input is classified as UPDATE_TASK with sufficient confidence
        """
        intent = self.classify(user_input)
        return intent.confidence >= threshold and 'task_id' in intent.parameters and intent.parameters['task_id'] is not None and intent.parameters['updates']

    def can_extract_task_id_and_updates(self, user_input: str) -> bool:
        """
        Check if both task ID and updates can be extracted from the user input.

        Args:
            user_input (str): The user's input string

        Returns:
            bool: True if both task ID and updates can be extracted, False otherwise
        """
        parameters = self._extract_update_task_parameters(user_input)
        return ('task_id' in parameters and parameters['task_id'] is not None and
                'updates' in parameters and parameters['updates'])