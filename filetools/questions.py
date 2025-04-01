import logging
import re
from typing import Optional

log = logging.getLogger("filetools")


class QuestionError(Exception):
    """Exception raised when there is an error processing a user question.

    Args:
        message: The error message
        question: Optional question that caused the error
        details: Optional additional error details

    Attributes:
        question: The question that caused the error
        details: Additional error context
    """

    def __init__(
        self: "QuestionError",
        message: str,
        question: str | None = None,
        details: str | None = None,
    ):
        super().__init__(message)
        self.question = question
        self.details = details
        log.error(f"QuestionError: {message} | Question: {question} | Details: {details}")

    def __str__(self: "QuestionError") -> str:
        return f"QuestionError: {self.args[0]} | Question: {self.question} | Details: {self.details}"


def ask_bool(question: str, default_value: bool | None = None) -> bool | None:
    """Prompt user with a yes/no question using consistent formatting.

    Args:
        question: The question to display to the user
        default_value: Value to return if user just presses Enter

    Returns:
        bool: True for 'yes', False for 'no', or default_value if Enter pressed
              with a default set

    Example:
        >>> ask_bool("Continue processing", default_value=True)
        Continue processing [y/n]? y
        True
    """
    prompt = f"{question} [y/n]? "

    while True:
        log.question(prompt)  # Logs the prompt in QUESTION (green)
        user_input = input("|| ").strip().lower()  # Keeps "|| " formatting

        if user_input in {"y", "yes"}:
            return True
        if user_input in {"n", "no"}:
            return False
        if user_input == "" and default_value is not None:
            return default_value

        log.warning(f"Invalid input: {user_input}. Expected 'y' or 'n'.")


def ask_multichoice(choices: list[str]) -> str:
    """Present numbered menu of choices and get user selection.

    Args:
        choices: List of options to present to user

    Returns:
        str: The selected choice text

    Raises:
        QuestionError: If choices list is empty

    Example:
        >>> ask_multichoice(["apple", "banana", "orange"])
        Choose an option (1, 2, 3):
        1) apple
        2) banana
        3) orange
        || 2
        'banana'
    """
    if not choices:
        raise QuestionError("No choices provided for ask_multichoice().")

    choice_dict: dict = {str(i + 1): choice for i, choice in enumerate(choices)}

    log.question(f"Choose an option ({', '.join(choice_dict.keys())}):")
    for key, value in choice_dict.items():
        log.info(f"{key}) {value}")

    while True:
        user_input = input("\n|| ").strip()

        if user_input in choice_dict:
            log.info(f"User selected choice {user_input}: {choice_dict[user_input]}")
            return choice_dict[user_input]

        log.warning(f"Invalid choice: {user_input}. Expected one of {list(choice_dict.keys())}.")
        log.warning(f"Invalid choice: {user_input}. Please enter a valid number from the list.")


def ask_text_input(qstring: str) -> str:
    """Get free-form text input from user.

    Args:
        qstring: Question prompt to display

    Returns:
        str: User's response:
            - converted to lowercase
            - leading/trailing whitespace removed
            - internal spaces replaced by single underscores
            - empty string if no input provided

    Example:
        >>> ask_text_input("Enter show name")
        Enter show name? The Office
        'the_office'
    """
    question = qstring + "? "
    log.question(question)
    answer = input("|| ").strip()  # Strip leading/trailing whitespace
    # Replace one or more spaces with single underscore
    return re.sub(r"\s+", "_", answer).lower()
