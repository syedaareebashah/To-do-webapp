"""
LIST_TASKS Intent Classifier for Todo AI Chatbot Agent

This module specifically handles classification of LIST_TASKS intents.
"""

from typing import Dict, Any
from ..models.intent import Intent, IntentType
from ..utils.confidence_scorer import get_confidence_score


class ListTasksClassifier:
    """
    Specialized classifier for LIST_TASKS intents.
    """

    def __init__(self):
        """
        Initialize the LIST_TASKS classifier.
        """
        self.keywords = [
            'show', 'list', 'view', 'display', 'see', 'get', 'fetch', 'find',
            'all', 'my', 'current', 'tasks', 'todos', 'to-dos', 'items',
            'what', 'have', 'got', 'remaining', 'pending', 'completed', 'done'
        ]

        self.filter_indicators = {
            'pending': ['pending', 'incomplete', 'left', 'remaining', 'unfinished', 'not done', 'to do'],
            'completed': ['completed', 'done', 'finished', 'completed', 'done with'],
            'all': ['all', 'every', 'all of', 'all my', 'entire', 'total'],
            'overdue': ['overdue', 'late', 'past due', 'missed', 'overdue']
        }

        self.sort_indicators = {
            'created_at': ['newest', 'oldest', 'first', 'last', 'recent'],
            'due_date': ['due', 'date', 'deadline', 'urgent', 'soon'],
            'priority': ['important', 'priority', 'urgent', 'high priority']
        }

    def classify(self, user_input: str) -> Intent:
        """
        Classify whether the input represents a LIST_TASKS intent.

        Args:
            user_input (str): The user's input string

        Returns:
            Intent: An Intent object with LIST_TASKS type and confidence score
        """
        confidence = self._calculate_list_tasks_confidence(user_input)

        # Extract parameters for listing tasks
        parameters = self._extract_list_tasks_parameters(user_input)

        intent = Intent(
            intent_type=IntentType.LIST_TASKS,
            confidence=confidence,
            parameters=parameters
        )

        return intent

    def _calculate_list_tasks_confidence(self, user_input: str) -> float:
        """
        Calculate the confidence that the input represents a LIST_TASKS intent.

        Args:
            user_input (str): The user's input string

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        # Use the general confidence scorer as a baseline
        baseline_confidence = get_confidence_score(user_input, 'list_tasks')

        input_lower = user_input.lower()

        # Check for presence of keywords
        keyword_matches = sum(1 for keyword in self.keywords if keyword in input_lower)

        # Boost confidence based on number of matches
        if keyword_matches >= 2:
            baseline_confidence = min(baseline_confidence + 0.2, 1.0)
        elif keyword_matches >= 1:
            baseline_confidence = min(baseline_confidence + 0.1, 1.0)

        # Boost confidence if we find strong indicators
        strong_indicators = ['show', 'list', 'view', 'see my', 'my tasks', 'what']
        if any(indicator in input_lower for indicator in strong_indicators):
            baseline_confidence = min(baseline_confidence + 0.15, 1.0)

        # Reduce confidence if the input seems to be requesting a different action
        # like adding, completing, or deleting
        other_action_indicators = ['add', 'create', 'complete', 'finish', 'delete', 'remove', 'update', 'change']
        if any(indicator in input_lower for indicator in other_action_indicators):
            baseline_confidence = max(baseline_confidence - 0.3, 0.0)

        return baseline_confidence

    def _extract_list_tasks_parameters(self, user_input: str) -> Dict[str, Any]:
        """
        Extract parameters specific to LIST_TASKS intent.

        Args:
            user_input (str): The original user input

        Returns:
            Dict[str, Any]: Extracted parameters for list tasks
        """
        import re

        parameters = {}

        # Determine filter based on user input
        user_lower = user_input.lower()

        # Check for specific filters
        for filter_type, filter_keywords in self.filter_indicators.items():
            if any(keyword in user_lower for keyword in filter_keywords):
                parameters['filter'] = filter_type
                break

        # If no specific filter was found, default to 'all'
        if 'filter' not in parameters:
            # Check for "all" or "my" which usually mean all tasks
            if any(word in user_lower for word in ['all', 'my', 'everything']):
                parameters['filter'] = 'all'
            # Check for questions about what user has to do (usually means pending)
            elif any(word in user_lower for word in ['what', 'have', 'got', 'left', 'remaining']):
                parameters['filter'] = 'pending'

        # Determine sort by
        for sort_type, sort_keywords in self.sort_indicators.items():
            if any(keyword in user_lower for keyword in sort_keywords):
                parameters['sort_by'] = sort_type
                break

        # Determine sort order
        if any(word in user_lower for word in ['newest', 'recent', 'first', 'top']):
            parameters['sort_order'] = 'desc'
        elif any(word in user_lower for word in ['oldest', 'earliest', 'last']):
            parameters['sort_order'] = 'asc'

        # Extract limit if specified
        limit_pattern = r'(?:top|first|last|limit to|show me)\s+(\d+)\s+(?:tasks?|items?)'
        limit_match = re.search(limit_pattern, user_lower)
        if limit_match:
            try:
                limit_val = int(limit_match.group(1))
                parameters['limit'] = min(limit_val, 100)  # Cap at 100
            except ValueError:
                pass

        # If no limit was specified, default to 50
        if 'limit' not in parameters:
            parameters['limit'] = 50

        # Extract additional context
        if any(word in user_lower for word in ['today', 'today\'s', 'daily']):
            parameters['date_filter'] = 'today'
        elif any(word in user_lower for word in ['week', 'weekly', 'this week']):
            parameters['date_filter'] = 'this_week'
        elif any(word in user_lower for word in ['month', 'monthly', 'this month']):
            parameters['date_filter'] = 'this_month'

        return parameters

    def is_list_tasks_intent(self, user_input: str, threshold: float = 0.5) -> bool:
        """
        Check if the input represents a LIST_TASKS intent with sufficient confidence.

        Args:
            user_input (str): The user's input string
            threshold (float): Confidence threshold for classification

        Returns:
            bool: True if the input is classified as LIST_TASKS with sufficient confidence
        """
        intent = self.classify(user_input)
        return intent.confidence >= threshold