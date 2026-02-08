"""
Test specific classifier to see if it works correctly.
"""

from src.classifiers.complete_task_classifier import CompleteTaskClassifier
from src.classifiers.add_task_classifier import AddTaskClassifier
from src.classifiers.delete_task_classifier import DeleteTaskClassifier


def test_specific_classifiers():
    """
    Test the specific classifiers individually.
    """
    print("Testing specific classifiers...")

    # Test cases
    test_cases = [
        "Complete task 1",
        "Finish task 2",
        "Delete task 3",
        "Remove task 4",
        "Add a task to buy groceries"
    ]

    # Initialize classifiers
    complete_classifier = CompleteTaskClassifier()
    add_classifier = AddTaskClassifier()
    delete_classifier = DeleteTaskClassifier()

    for user_input in test_cases:
        print(f"\nInput: '{user_input}'")

        # Test each specific classifier
        complete_intent = complete_classifier.classify(user_input)
        add_intent = add_classifier.classify(user_input)
        delete_intent = delete_classifier.classify(user_input)

        print(f"  Complete classifier: {complete_intent.type.value} with confidence {complete_intent.confidence:.3f}")
        print(f"  Add classifier: {add_intent.type.value} with confidence {add_intent.confidence:.3f}")
        print(f"  Delete classifier: {delete_intent.type.value} with confidence {delete_intent.confidence:.3f}")

        # Determine winner
        classifiers_results = [
            ("Complete", complete_intent.confidence),
            ("Add", add_intent.confidence),
            ("Delete", delete_intent.confidence)
        ]

        winner = max(classifiers_results, key=lambda x: x[1])
        print(f"  Winner: {winner[0]} with confidence {winner[1]:.3f}")


if __name__ == "__main__":
    test_specific_classifiers()