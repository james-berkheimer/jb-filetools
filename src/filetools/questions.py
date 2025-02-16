from typing import Dict, List, Optional

from .logging import setup_logger

log = setup_logger(__name__)  # Standardized logger


class QuestionError(Exception):
    """Raised when there is an error processing a user question."""

    def __init__(self, message: str, question: Optional[str] = None, details: Optional[str] = None):
        super().__init__(message)
        self.question = question
        self.details = details
        log.error(f"QuestionError: {message} | Question: {question} | Details: {details}")

    def __str__(self):
        return f"QuestionError: {self.args[0]} | Question: {self.question} | Details: {self.details}"


def ask_bool(question: str, default_value: Optional[bool] = None) -> Optional[bool]:
    """
    Prompts the user with a yes/no question.

    Args:
        question (str): The question to ask.
        default_value (Optional[bool]): The default answer if the user presses Enter.

    Returns:
        Optional[bool]: True for 'yes', False for 'no', or the default_value.
    """
    prompt = f"{question} [y/n]? "

    while True:
        log.question(prompt)
        user_input = input(prompt).strip().lower()

        if user_input in {"y", "yes"}:
            return True
        if user_input in {"n", "no"}:
            return False
        if user_input == "" and default_value is not None:
            return default_value

        log.warning(f"Invalid input: {user_input}. Expected 'y' or 'n'.")


def ask_multichoice(choices: List[str]) -> str:
    """
    Prompts the user to choose from a list of options.

    Args:
        choices (List[str]): A list of string choices.

    Returns:
        str: The chosen option.

    Raises:
        QuestionError: If no choices are provided.
    """
    if not choices:
        raise QuestionError("No choices provided for ask_multichoice().")

    choice_dict: Dict[str, str] = {str(i + 1): choice for i, choice in enumerate(choices)}

    log.question(f"Choose an option ({', '.join(choice_dict.keys())}):")
    for key, value in choice_dict.items():
        print(f"{key}) {value}")

    while True:
        user_input = input("\nEnter the number of your choice: ").strip()

        if user_input in choice_dict:
            log.info(f"User selected choice {user_input}: {choice_dict[user_input]}")
            return choice_dict[user_input]

        log.warning(f"Invalid choice: {user_input}. Expected one of {list(choice_dict.keys())}.")
        print(f"Invalid choice: {user_input}. Please enter a valid number from the list.")
