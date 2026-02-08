"""
Natural Language Processor for Todo AI Chatbot Agent

This module processes user input to prepare it for intent classification.
"""

import re
from typing import Dict, Any, List
from ..models.conversation_context import ConversationContext


class NLPProcessor:
    """
    Natural Language Processor for the Todo AI Chatbot Agent.
    This class processes user input to prepare it for intent classification.
    """

    def __init__(self):
        """
        Initialize the NLP processor with common patterns and transformations.
        """
        # Define common contractions and their expansions
        self.contractions = {
            "won't": "will not",
            "can't": "cannot",
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would",
            "'m": " am"
        }

        # Define common synonyms that map to the same intent
        self.synonyms = {
            'add': ['create', 'make', 'add', 'schedule', 'new'],
            'list': ['show', 'list', 'view', 'display', 'see', 'get'],
            'complete': ['complete', 'finish', 'done', 'mark as done', 'check'],
            'delete': ['delete', 'remove', 'cancel', 'erase', 'eliminate'],
            'update': ['update', 'change', 'modify', 'edit', 'adjust']
        }

    def process(self, user_input: str, conversation_context: ConversationContext = None) -> Dict[str, Any]:
        """
        Process user input to prepare it for intent classification.

        Args:
            user_input (str): The raw user input
            conversation_context (ConversationContext): Context from the conversation (optional)

        Returns:
            Dict[str, Any]: Processed input with relevant features
        """
        # Normalize the input
        normalized_input = self._normalize_text(user_input)

        # Tokenize the input
        tokens = self._tokenize(normalized_input)

        # Extract features
        features = self._extract_features(normalized_input, tokens)

        # Identify potential intent keywords
        intent_keywords = self._identify_intent_keywords(normalized_input)

        # Get context from conversation if provided
        context_features = {}
        if conversation_context:
            context_features = self._extract_context_features(conversation_context)

        # Combine all features
        processed_data = {
            'original_input': user_input,
            'normalized_input': normalized_input,
            'tokens': tokens,
            'features': features,
            'intent_keywords': intent_keywords,
            'context_features': context_features,
            'processed_at': self._get_timestamp()
        }

        return processed_data

    def _normalize_text(self, text: str) -> str:
        """
        Normalize text by expanding contractions, converting to lowercase, etc.

        Args:
            text (str): The input text to normalize

        Returns:
            str: Normalized text
        """
        # Convert to lowercase
        text = text.lower()

        # Expand contractions
        for contraction, expansion in self.contractions.items():
            text = text.replace(contraction, expansion)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize the input text into individual words/tokens.

        Args:
            text (str): The text to tokenize

        Returns:
            List[str]: List of tokens
        """
        # Split on whitespace and punctuation
        tokens = re.split(r'[^\w\'-]+', text)

        # Remove empty tokens
        tokens = [token for token in tokens if token]

        return tokens

    def _extract_features(self, normalized_input: str, tokens: List[str]) -> Dict[str, Any]:
        """
        Extract relevant features from the normalized input.

        Args:
            normalized_input (str): The normalized input text
            tokens (List[str]): The list of tokens

        Returns:
            Dict[str, Any]: Dictionary of extracted features
        """
        features = {
            'length': len(normalized_input),
            'word_count': len(tokens),
            'has_question_mark': '?' in normalized_input,
            'has_exclamation': '!' in normalized_input,
            'starts_with_action': self._starts_with_action_word(normalized_input),
            'contains_task_related': self._contains_task_related_words(normalized_input),
            'sentence_structure': self._analyze_sentence_structure(normalized_input)
        }

        return features

    def _starts_with_action_word(self, text: str) -> bool:
        """
        Check if the text starts with an action word.

        Args:
            text (str): The input text

        Returns:
            bool: True if text starts with an action word, False otherwise
        """
        # Split into words and get the first word
        words = text.split()
        if not words:
            return False

        first_word = words[0]
        action_words = ['add', 'create', 'show', 'list', 'complete', 'finish', 'delete', 'remove', 'update', 'change']

        return first_word in action_words

    def _contains_task_related_words(self, text: str) -> bool:
        """
        Check if the text contains task-related words.

        Args:
            text (str): The input text

        Returns:
            bool: True if text contains task-related words, False otherwise
        """
        task_related_words = ['task', 'todo', 'to-do', 'item', 'thing', 'job', 'assignment', 'chore', 'work']

        # Convert to lowercase for comparison
        text_lower = text.lower()

        for word in task_related_words:
            if word in text_lower:
                return True

        return False

    def _analyze_sentence_structure(self, text: str) -> str:
        """
        Analyze the sentence structure of the input text.

        Args:
            text (str): The input text

        Returns:
            str: The identified sentence structure type
        """
        if text.endswith('?'):
            return 'question'
        elif text.endswith('!'):
            return 'exclamation'
        else:
            return 'statement'

    def _identify_intent_keywords(self, text: str) -> Dict[str, List[str]]:
        """
        Identify potential intent-related keywords in the text.

        Args:
            text (str): The input text

        Returns:
            Dict[str, List[str]]: Dictionary mapping intent types to found keywords
        """
        # Tokenize the text again for keyword matching
        tokens = self._tokenize(text)

        found_keywords = {
            'add_task': [],
            'list_tasks': [],
            'complete_task': [],
            'delete_task': [],
            'update_task': []
        }

        # Look for intent-related keywords in the tokens
        for token in tokens:
            if token in self.synonyms['add']:
                found_keywords['add_task'].append(token)
            elif token in self.synonyms['list']:
                found_keywords['list_tasks'].append(token)
            elif token in self.synonyms['complete']:
                found_keywords['complete_task'].append(token)
            elif token in self.synonyms['delete']:
                found_keywords['delete_task'].append(token)
            elif token in self.synonyms['update']:
                found_keywords['update_task'].append(token)

        return found_keywords

    def _extract_context_features(self, conversation_context: ConversationContext) -> Dict[str, Any]:
        """
        Extract features from the conversation context.

        Args:
            conversation_context (ConversationContext): The conversation context

        Returns:
            Dict[str, Any]: Dictionary of context features
        """
        context_features = {
            'previous_user_inputs': conversation_context.get_user_inputs()[-3:],  # Last 3 user inputs
            'previous_agent_responses': conversation_context.get_agent_responses()[-3:],  # Last 3 agent responses
            'active_tasks_count': len(conversation_context.active_tasks),
            'total_turns': len(conversation_context.turns),
            'conversation_state': conversation_context.state.value
        }

        return context_features

    def _get_timestamp(self) -> str:
        """
        Get the current timestamp.

        Returns:
            str: The current timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()

    def preprocess_for_classification(self, user_input: str, conversation_context: ConversationContext = None) -> Dict[str, Any]:
        """
        Preprocess user input specifically for intent classification.

        Args:
            user_input (str): The raw user input
            conversation_context (ConversationContext): Context from the conversation (optional)

        Returns:
            Dict[str, Any]: Preprocessed data suitable for classification
        """
        # Process the input normally
        processed = self.process(user_input, conversation_context)

        # Add additional features specifically for classification
        classification_features = {
            'input_length': len(user_input),
            'has_numbers': bool(re.search(r'\d+', user_input)),
            'keyword_density': self._calculate_keyword_density(processed['intent_keywords']),
            'ambiguity_indicators': self._find_ambiguity_indicators(user_input)
        }

        # Update the processed data with classification features
        processed.update(classification_features)

        return processed

    def _calculate_keyword_density(self, intent_keywords: Dict[str, List[str]]) -> float:
        """
        Calculate the density of intent-related keywords in the input.

        Args:
            intent_keywords (Dict[str, List[str]]): Found intent keywords

        Returns:
            float: Keyword density score
        """
        total_keywords = sum(len(keywords) for keywords in intent_keywords.values())

        # If no keywords found, return 0
        if total_keywords == 0:
            return 0.0

        # Calculate density as a proportion of total found keywords
        # Higher density suggests stronger intent signal
        return min(total_keywords / 10.0, 1.0)  # Cap at 1.0

    def _find_ambiguity_indicators(self, text: str) -> List[str]:
        """
        Find indicators of ambiguity in the user input.

        Args:
            text (str): The input text

        Returns:
            List[str]: List of ambiguity indicators found
        """
        ambiguity_patterns = [
            r'unclear|not sure|maybe|perhaps|possibly',
            r'what.*is|who.*is|where.*is|how.*is',
            r'that one|the other|this|that',
            r'can you|could you|would you',
            r'please|kindly|if you would'
        ]

        found_indicators = []
        text_lower = text.lower()

        for pattern in ambiguity_patterns:
            matches = re.findall(pattern, text_lower)
            found_indicators.extend(matches)

        return found_indicators