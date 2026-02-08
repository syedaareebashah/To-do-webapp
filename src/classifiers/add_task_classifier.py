"""
ADD_TASK Intent Classifier for Todo AI Chatbot Agent

This module specifically handles classification of ADD_TASK intents.
"""

from typing import Dict, Any
from ..models.intent import Intent, IntentType
from ..utils.confidence_scorer import get_confidence_score


class AddTaskClassifier:
    """
    Specialized classifier for ADD_TASK intents.
    """

    def __init__(self):
        """
        Initialize the ADD_TASK classifier.
        """
        self.keywords = [
            'add', 'create', 'make', 'remember', 'schedule', 'new',
            'task', 'todo', 'to-do', 'item', 'need to', 'want to',
            'should', 'have to', 'must'
        ]

        self.content_indicators = [
            'to', 'for', 'about', 'that', 'is', 'should'
        ]

    def classify(self, user_input: str) -> Intent:
        """
        Classify whether the input represents an ADD_TASK intent.

        Args:
            user_input (str): The user's input string

        Returns:
            Intent: An Intent object with ADD_TASK type and confidence score
        """
        confidence = self._calculate_add_task_confidence(user_input)

        # Extract task content from the input
        parameters = self._extract_add_task_parameters(user_input)

        intent = Intent(
            intent_type=IntentType.ADD_TASK,
            confidence=confidence,
            parameters=parameters
        )

        return intent

    def _calculate_add_task_confidence(self, user_input: str) -> float:
        """
        Calculate the confidence that the input represents an ADD_TASK intent.

        Args:
            user_input (str): The user's input string

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        # Use the general confidence scorer as a baseline
        baseline_confidence = get_confidence_score(user_input, 'add_task')

        # Apply additional heuristics to refine the confidence

        # Check for presence of keywords
        input_lower = user_input.lower()
        keyword_matches = sum(1 for keyword in self.keywords if keyword in input_lower)

        # Boost confidence if we find action keywords
        if any(kw in input_lower for kw in ['add', 'create', 'make', 'new']):
            baseline_confidence = min(baseline_confidence + 0.1, 1.0)

        # Boost confidence if we find content indicators
        if any(indicator in input_lower for indicator in self.content_indicators):
            baseline_confidence = min(baseline_confidence + 0.1, 1.0)

        # Boost confidence if the input seems to have task content after action words
        if self._appears_to_have_task_content(input_lower):
            baseline_confidence = min(baseline_confidence + 0.1, 1.0)

        # Reduce confidence if the input seems more like a question or request for info
        if '?' in user_input or any(qw in input_lower for qw in ['what', 'how', 'when', 'where', 'who', 'why']):
            baseline_confidence = max(baseline_confidence - 0.2, 0.0)

        return baseline_confidence

    def _appears_to_have_task_content(self, input_lower: str) -> bool:
        """
        Check if the input appears to have task content after action words.

        Args:
            input_lower (str): The lowercase input string

        Returns:
            bool: True if the input appears to have task content
        """
        import re

        # Look for patterns that indicate task content follows
        patterns = [
            r'(?:add|create|make|add|schedule)\s+(?:a\s+)?(?:task|to-do|todo)\s+(?:to|for|about|that|is)\s+.+',
            r'(?:add|create|make|add|schedule)\s+(?:a\s+)?(?:task|to-do|todo)\s+.+',
            r'(?:remind\s+me\s+to|need\s+to|want\s+to|should|have\s+to|must)\s+.+',
        ]

        for pattern in patterns:
            if re.search(pattern, input_lower):
                return True

        # If no clear pattern, check if there's substantial content after common action words
        parts = input_lower.split()
        if len(parts) > 3:  # If there's more than just an action word
            action_words = {'add', 'create', 'make', 'new', 'schedule'}
            non_action_content = [word for word in parts[1:] if word not in action_words and len(word) > 2]
            return len(non_action_content) >= 2

        return False

    def _extract_add_task_parameters(self, user_input: str) -> Dict[str, Any]:
        """
        Extract parameters specific to ADD_TASK intent.

        Args:
            user_input (str): The original user input

        Returns:
            Dict[str, Any]: Extracted parameters for add task
        """
        import re

        parameters = {}

        # Extract task content using various patterns
        patterns = [
            # Pattern: "add task to [content]", "create task [content]", etc.
            r'(?:add|create|make|add|schedule)\s+(?:a\s+)?(?:task|to-do|todo)\s+(?:to|for|about|that|is)\s+(.+)',
            r'(?:add|create|make|add|schedule)\s+(?:a\s+)?(?:task|to-do|todo)\s+(.+)',
            # Pattern: "remind me to [content]", "need to [content]", etc.
            r'(?:remind\s+me\s+to|need\s+to|want\s+to|should|have\s+to|must)\s+(.+)',
        ]

        task_content = ""
        for pattern in patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                task_content = match.group(1).strip()
                break

        # If no pattern matched, try to extract content differently
        if not task_content:
            # Remove common action words to get the content
            clean_input = re.sub(r'^(?:add|create|make|add|schedule|new|task|to-do|todo)\s*', '', user_input, flags=re.IGNORECASE)
            task_content = clean_input.strip()

            # If it still starts with action words, try another approach
            if not task_content and len(user_input.split()) > 2:
                # Take everything after the first 2-3 words as content
                words = user_input.split()
                task_content = ' '.join(words[min(2, len(words)-1):]).strip()

        if task_content:
            parameters['task_content'] = task_content
        else:
            # Use the whole input as content if nothing else works, but try to clean it
            clean_content = re.sub(r'^(?:add|create|make|new|task|to-do|todo|schedule)\s*', '', user_input, flags=re.IGNORECASE).strip()
            parameters['task_content'] = clean_content if clean_content else user_input

        # Extract due date if mentioned
        date_patterns = [
            r'(?:by|before|on|until)\s+(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?|\w+\s+\d{1,2}(?:,\s*\d{4})?|\d{1,2}\s+\w+(?:\s+\d{4})?)',
            r'(?:in|within)\s+(\d+\s+(?:days?|weeks?|months?|hours?|minutes?))'
        ]

        for date_pattern in date_patterns:
            date_match = re.search(date_pattern, user_input, re.IGNORECASE)
            if date_match:
                parameters['due_date'] = date_match.group(1)
                break

        # Extract priority if mentioned
        priority_pattern = r'(?:with\s+)?(high|medium|low)\s+(?:priority|priority)'
        priority_match = re.search(priority_pattern, user_input, re.IGNORECASE)
        if priority_match:
            parameters['priority'] = priority_match.group(1).lower()

        # Extract tags if mentioned
        tag_pattern = r'(?:with\s+tag|tagged\s+as|labeled\s+as)\s+(.+)'
        tag_match = re.search(tag_pattern, user_input, re.IGNORECASE)
        if tag_match:
            tags = [tag.strip() for tag in tag_match.group(1).split(',')]
            parameters['tags'] = tags

        return parameters

    def is_add_task_intent(self, user_input: str, threshold: float = 0.5) -> bool:
        """
        Check if the input represents an ADD_TASK intent with sufficient confidence.

        Args:
            user_input (str): The user's input string
            threshold (float): Confidence threshold for classification

        Returns:
            bool: True if the input is classified as ADD_TASK with sufficient confidence
        """
        intent = self.classify(user_input)
        return intent.confidence >= threshold