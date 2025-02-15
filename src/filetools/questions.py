# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import re
import sys
from typing import Any, Dict, List


# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
class QuestionError(Exception):
    pass


# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------


def ask_bool(question: str, default_value: Any = None) -> Any:
    answer = None
    prompt = question + " [y/n]? "
    while True:
        print("")
        user_input = input(prompt)
        if re.match("y", user_input, re.IGNORECASE):
            answer = True
            break
        elif re.match("n", user_input, re.IGNORECASE):
            answer = False
            break
        elif not user_input.strip() and default_value is not None:
            answer = default_value
            break
        else:
            continue
    return answer


def ask_multichoice(choices: List[str]) -> str:
    prompt = ""
    choice_dict: Dict[str, str] = {}
    # Let's form the question to present to the user
    try:
        choice_dict = {str(i + 1): choices[i] for i in range(len(choices))}
        for key, value in choice_dict.items():
            prompt += f"{key}) {value}\n"
    except Exception as error:
        import traceback

        tb = traceback.extract_tb(sys.exc_info()[2], limit=1)[0]
        raise QuestionError(f"{tb} : {str(error)}") from error

    # Wait for the user input
    while True:
        user_input = input(prompt)
        if user_input in choice_dict:
            return choice_dict[user_input]
        else:
            print(f"\n{user_input} is not a choice.....please choose again\n")
            continue
