"""
Intent Classifier for Todo AI Chatbot Agent

This module classifies user intent based on processed input.
"""

from typing import Dict, Any, Optional
from ..models.intent import Intent, IntentType
from ..models.conversation_context import ConversationContext
from ..utils.confidence_scorer import get_all_confidences
from ..config.logging_config import logger


class IntentClassifier:
    """
    Classifies user intent based on processed input.
    """

    def __init__(self, threshold: float = 0.7):
        """
        Initialize the intent classifier.

        Args:
            threshold (float): Confidence threshold for classification (default: 0.7)
        """
        self.threshold = threshold

    def classify(self, processed_input: Dict[str, Any], conversation_context: ConversationContext = None) -> Intent:
        """
        Classify the user's intent based on processed input.

        Args:
            processed_input (Dict[str, Any]): The processed input from NLPProcessor
            conversation_context (ConversationContext): Context from the conversation (optional)

        Returns:
            Intent: The classified intent with confidence score
        """
        # Extract original user input
        user_input = processed_input.get('original_input', '')

        # Use specific classifiers for more accurate intent determination
        from src.classifiers.add_task_classifier import AddTaskClassifier
        from src.classifiers.list_tasks_classifier import ListTasksClassifier
        from src.classifiers.complete_task_classifier import CompleteTaskClassifier
        from src.classifiers.delete_task_classifier import DeleteTaskClassifier
        from src.classifiers.update_task_classifier import UpdateTaskClassifier

        # Initialize specific classifiers
        classifiers = {
            'add_task': AddTaskClassifier(),
            'list_tasks': ListTasksClassifier(),
            'complete_task': CompleteTaskClassifier(),
            'delete_task': DeleteTaskClassifier(),
            'update_task': UpdateTaskClassifier()
        }

        # Get confidence scores from specific classifiers
        specific_confidences = {}
        for intent_name, classifier in classifiers.items():
            try:
                specific_intent = classifier.classify(user_input)
                specific_confidences[intent_name] = specific_intent.confidence
            except Exception:
                # If specific classifier fails, use 0.0 confidence
                specific_confidences[intent_name] = 0.0

        # Define priority order for intents (more specific take precedence over generic)
        # ADD_TASK is lowest priority as it's a catch-all for task creation
        priority_order = [
            'complete_task',  # Most specific - clear action to complete
            'delete_task',    # Most specific - clear action to delete
            'update_task',    # Specific - action to update
            'list_tasks',     # Specific - action to list
            'add_task'        # Least specific - catch-all for adding
        ]

        # Find the highest confidence intent among those that meet threshold
        # with priority consideration
        best_intent_type = 'add_task'  # Default fallback
        best_confidence = 0.0

        # First, check if any high-priority intent meets the threshold
        for intent_type in priority_order:
            confidence = specific_confidences.get(intent_type, 0.0)
            if confidence >= self.threshold:
                best_intent_type = intent_type
                best_confidence = confidence
                # Break to give priority to the first high-confidence match
                break

        # If no intent meets the threshold, use the one with highest confidence overall
        if best_confidence < self.threshold:
            overall_best_intent = max(specific_confidences, key=specific_confidences.get)
            overall_best_confidence = specific_confidences[overall_best_intent]

            if overall_best_confidence >= self.threshold:
                best_intent_type = overall_best_intent
                best_confidence = overall_best_confidence
            else:
                # If no intent meets the threshold, classify as ambiguous
                best_intent_type = 'ambiguous'
                best_confidence = overall_best_confidence

        # Determine the intent type
        if best_intent_type == 'ambiguous':
            intent_type = IntentType.AMBIGUOUS
        else:
            intent_type = IntentType(best_intent_type.upper())

        confidence = best_confidence

        # Extract parameters from the processed input
        parameters = self._extract_parameters(processed_input, intent_type)

        # Create and return the Intent object
        intent = Intent(
            intent_type=intent_type,
            confidence=confidence,
            parameters=parameters
        )

        logger.info(f"Classified intent: {intent_type.value} with confidence: {confidence:.2f}")

        return intent

    def _has_tie(self, confidence_scores: Dict[str, float], best_confidence: float) -> bool:
        """
        Check if there are multiple intents with the same highest confidence.

        Args:
            confidence_scores (Dict[str, float]): Dictionary of intent types and their confidence scores
            best_confidence (float): The highest confidence score

        Returns:
            bool: True if there are ties, False otherwise
        """
        # Count how many intents have the best confidence
        tie_count = sum(1 for score in confidence_scores.values() if score == best_confidence)
        return tie_count > 1

    def _resolve_tie(self, user_input: str, processed_input: Dict[str, Any], confidence_scores: Dict[str, float]) -> IntentType:
        """
        Resolve ties between intents with the same confidence.

        Args:
            user_input (str): Original user input
            processed_input (Dict[str, Any]): Processed input data
            confidence_scores (Dict[str, float]): Dictionary of intent types and their confidence scores

        Returns:
            IntentType: The resolved intent type
        """
        # Import specific classifiers to make more accurate determination
        from .add_task_classifier import AddTaskClassifier
        from .list_tasks_classifier import ListTasksClassifier
        from .complete_task_classifier import CompleteTaskClassifier
        from .delete_task_classifier import DeleteTaskClassifier
        from .update_task_classifier import UpdateTaskClassifier

        # Get all intents with the highest confidence
        best_confidence = max(confidence_scores.values())
        tied_intents = [intent for intent, score in confidence_scores.items() if score == best_confidence]

        # Use specific classifiers to determine the best intent
        classifiers = {
            'add_task': AddTaskClassifier(),
            'list_tasks': ListTasksClassifier(),
            'complete_task': CompleteTaskClassifier(),
            'delete_task': DeleteTaskClassifier(),
            'update_task': UpdateTaskClassifier()
        }

        # Get specific confidence scores from individual classifiers
        specific_scores = {}
        for intent_type in tied_intents:
            if intent_type in classifiers:
                specific_intent = classifiers[intent_type].classify(user_input)
                specific_scores[intent_type] = specific_intent.confidence

        # If we have specific scores, pick the highest one
        if specific_scores:
            best_specific_intent = max(specific_scores, key=specific_scores.get)
            return IntentType(best_specific_intent.upper())
        else:
            # If specific classification fails, fall back to original logic
            # But prioritize non-add_task intents when there's a tie
            # This is a heuristic: if complete_task and add_task have same confidence,
            # prefer complete_task as it's more specific to the user's intent
            priority_order = [
                'complete_task',  # Complete is more specific than add
                'delete_task',    # Delete is more specific than add
                'update_task',    # Update is more specific than add
                'list_tasks',     # List is more specific than add
                'add_task'        # Add is the default catch-all
            ]

            for intent_type in priority_order:
                if intent_type in tied_intents:
                    return IntentType(intent_type.upper())

        # Fallback to the original best intent
        return IntentType(max(confidence_scores, key=confidence_scores.get).upper())

    def _extract_parameters(self, processed_input: Dict[str, Any], intent_type: IntentType) -> Dict[str, Any]:
        """
        Extract relevant parameters from the processed input based on intent type.

        Args:
            processed_input (Dict[str, Any]): The processed input from NLPProcessor
            intent_type (IntentType): The classified intent type

        Returns:
            Dict[str, Any]: Extracted parameters
        """
        parameters = {}
        original_input = processed_input.get('original_input', '')

        # Extract parameters based on intent type
        if intent_type == IntentType.ADD_TASK:
            parameters = self._extract_add_task_parameters(original_input)
        elif intent_type == IntentType.LIST_TASKS:
            parameters = self._extract_list_tasks_parameters(original_input)
        elif intent_type == IntentType.COMPLETE_TASK:
            parameters = self._extract_complete_task_parameters(original_input, processed_input)
        elif intent_type == IntentType.DELETE_TASK:
            parameters = self._extract_delete_task_parameters(original_input, processed_input)
        elif intent_type == IntentType.UPDATE_TASK:
            parameters = self._extract_update_task_parameters(original_input, processed_input)
        elif intent_type == IntentType.AMBIGUOUS:
            parameters = self._extract_ambiguous_parameters(original_input)

        # Add context-based parameters if available
        if 'context_features' in processed_input:
            context_params = self._extract_context_parameters(processed_input['context_features'])
            parameters.update(context_params)

        return parameters

    def _extract_add_task_parameters(self, user_input: str) -> Dict[str, Any]:
        """
        Extract parameters for ADD_TASK intent.

        Args:
            user_input (str): The original user input

        Returns:
            Dict[str, Any]: Extracted parameters for add task
        """
        parameters = {}

        # Extract task content (everything after common action words)
        import re

        # Look for patterns like "add task to [content]", "create task [content]", etc.
        patterns = [
            r'(?:add|create|make|add|schedule)\s+(?:a\s+)?(?:task|to-do|todo)\s+(?:to|for|about|that|is)\s+(.+)',
            r'(?:add|create|make|add|schedule)\s+(?:a\s+)?(?:task|to-do|todo)\s+(.+)',
            r'(?:remind\s+me\s+to|need\s+to|want\s+to)\s+(.+)',
        ]

        task_content = ""
        for pattern in patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                task_content = match.group(1).strip()
                break

        # If no pattern matched, use the whole input minus common action words
        if not task_content:
            # Remove common action words to get the content
            clean_input = re.sub(r'^(?:add|create|make|add|schedule|new)\s+(?:a\s+)?(?:task|to-do|todo)\s*', '', user_input, flags=re.IGNORECASE)
            task_content = clean_input.strip()

        if task_content:
            parameters['task_content'] = task_content
        else:
            parameters['task_content'] = user_input  # Use the whole input as content if nothing else works

        # Extract due date if mentioned
        date_pattern = r'(?:by|before|on|until)\s+(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?|\w+\s+\d{1,2}(?:,\s*\d{4})?|\d{1,2}\s+\w+(?:\s+\d{4})?)'
        date_match = re.search(date_pattern, user_input, re.IGNORECASE)
        if date_match:
            parameters['due_date'] = date_match.group(1)

        # Extract priority if mentioned
        priority_pattern = r'(?:with\s+)?(?:high|medium|low)\s+(?:priority|priority)'
        priority_match = re.search(priority_pattern, user_input, re.IGNORECASE)
        if priority_match:
            priority_word = re.search(r'(high|medium|low)', priority_match.group(0), re.IGNORECASE)
            if priority_word:
                parameters['priority'] = priority_word.group(1).lower()

        return parameters

    def _extract_list_tasks_parameters(self, user_input: str) -> Dict[str, Any]:
        """
        Extract parameters for LIST_TASKS intent.

        Args:
            user_input (str): The original user input

        Returns:
            Dict[str, Any]: Extracted parameters for list tasks
        """
        parameters = {}

        # Determine filter based on user input
        user_lower = user_input.lower()

        if 'pending' in user_lower or 'incomplete' in user_lower:
            parameters['filter'] = 'pending'
        elif 'completed' in user_lower or 'done' in user_lower:
            parameters['filter'] = 'completed'
        elif 'overdue' in user_lower:
            parameters['filter'] = 'overdue'
        elif 'all' in user_lower:
            parameters['filter'] = 'all'

        # Determine sort order
        if 'oldest' in user_lower:
            parameters['sort_order'] = 'asc'
        elif 'newest' in user_lower or 'recent' in user_lower:
            parameters['sort_order'] = 'desc'

        # Determine sort by
        if 'priority' in user_lower:
            parameters['sort_by'] = 'priority'
        elif 'date' in user_lower or 'due' in user_lower:
            parameters['sort_by'] = 'due_date'

        return parameters

    def _extract_complete_task_parameters(self, user_input: str, processed_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract parameters for COMPLETE_TASK intent.

        Args:
            user_input (str): The original user input
            processed_input (Dict[str, Any]): The processed input

        Returns:
            Dict[str, Any]: Extracted parameters for complete task
        """
        parameters = {}

        # Extract task ID from the input
        import re

        # Look for task numbers or IDs
        number_pattern = r'(?:task|number|#)\s*(\d+)'
        number_match = re.search(number_pattern, user_input, re.IGNORECASE)
        if number_match:
            parameters['task_id'] = f"task_{number_match.group(1)}"
        else:
            # Try to extract just numbers from the input
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                # Use the first number as the task ID
                parameters['task_id'] = f"task_{numbers[0]}"

        # If no task ID was found, look in context for recent tasks
        if 'context_features' in processed_input:
            context_tasks = processed_input['context_features'].get('active_tasks_count', 0)
            if context_tasks > 0:
                # This would need more sophisticated context handling
                pass

        return parameters

    def _extract_delete_task_parameters(self, user_input: str, processed_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract parameters for DELETE_TASK intent.

        Args:
            user_input (str): The original user input
            processed_input (Dict[str, Any]): The processed input

        Returns:
            Dict[str, Any]: Extracted parameters for delete task
        """
        parameters = {}

        # Extract task ID from the input
        import re

        # Look for task numbers or IDs
        number_pattern = r'(?:task|number|#)\s*(\d+)'
        number_match = re.search(number_pattern, user_input, re.IGNORECASE)
        if number_match:
            parameters['task_id'] = f"task_{number_match.group(1)}"
        else:
            # Try to extract just numbers from the input
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                # Use the first number as the task ID
                parameters['task_id'] = f"task_{numbers[0]}"

        return parameters

    def _extract_update_task_parameters(self, user_input: str, processed_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract parameters for UPDATE_TASK intent.

        Args:
            user_input (str): The original user input
            processed_input (Dict[str, Any]): The processed input

        Returns:
            Dict[str, Any]: Extracted parameters for update task
        """
        parameters = {'updates': {}}

        # Extract task ID from the input
        import re

        # Look for task numbers or IDs
        number_pattern = r'(?:task|number|#)\s*(\d+)'
        number_match = re.search(number_pattern, user_input, re.IGNORECASE)
        if number_match:
            parameters['task_id'] = f"task_{number_match.group(1)}"
        else:
            # Try to extract just numbers from the input
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                # Use the first number as the task ID
                parameters['task_id'] = f"task_{numbers[0]}"

        # Extract what needs to be updated
        # Look for content updates
        content_pattern = r'(?:change|update|modify|edit)\s+(?:content|text|description)\s+to\s+(.+?)(?:\s+and|\s+with|$)'
        content_match = re.search(content_pattern, user_input, re.IGNORECASE)
        if content_match:
            parameters['updates']['content'] = content_match.group(1).strip()

        # Look for priority updates
        priority_pattern = r'(?:change|update|set)\s+(?:priority|importance)\s+to\s+(high|medium|low)'
        priority_match = re.search(priority_pattern, user_input, re.IGNORECASE)
        if priority_match:
            parameters['updates']['priority'] = priority_match.group(1).lower()

        # Look for status updates
        status_pattern = r'(?:change|update|set)\s+(?:status|state)\s+to\s+(pending|completed|incomplete)'
        status_match = re.search(status_pattern, user_input, re.IGNORECASE)
        if status_match:
            parameters['updates']['status'] = status_match.group(1).lower()

        return parameters

    def _extract_ambiguous_parameters(self, user_input: str) -> Dict[str, Any]:
        """
        Extract parameters for AMBIGUOUS intent.

        Args:
            user_input (str): The original user input

        Returns:
            Dict[str, Any]: Extracted parameters for ambiguous input
        """
        parameters = {
            'original_input': user_input,
            'reason': 'Insufficient confidence in intent classification'
        }
        return parameters

    def _extract_context_parameters(self, context_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract parameters from conversation context.

        Args:
            context_features (Dict[str, Any]): Context features from conversation

        Returns:
            Dict[str, Any]: Extracted context parameters
        """
        parameters = {}

        # Add active tasks if any
        if 'active_tasks_count' in context_features and context_features['active_tasks_count'] > 0:
            parameters['context_has_active_tasks'] = True

        # Add conversation state
        if 'conversation_state' in context_features:
            parameters['conversation_state'] = context_features['conversation_state']

        return parameters

    def set_threshold(self, threshold: float):
        """
        Set the confidence threshold for classification.

        Args:
            threshold (float): New confidence threshold
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")

        self.threshold = threshold

    def get_threshold(self) -> float:
        """
        Get the current confidence threshold.

        Returns:
            float: Current confidence threshold
        """
        return self.threshold