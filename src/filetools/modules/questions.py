#!/usr/bin/env python
#
# modules/questions.py
#
# This file will store question methods for user input
#

# --------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------
import re, sys
from typing import Any

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
class QuestionExceptions(Exception):    
    pass

# --------------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------------

def ask_bool(qbool:bool, default_value: Any = None) -> Any:
    answer = None
    question = qbool + " [y/n]? "
    while True:
        print("")
        user_input = input(question)
        if re.match("y", user_input):
            answer = True
            break
        elif re.match("n", user_input):
            answer = False
            break
        elif  not user_input.strip() and default_value is not None:
            answer = default_value
            break
        else:
            continue   
    return answer

def ask_multichoice(qlist: list):
    qstring = ""
    qdict = {}
    # Let's form the question to present to the user
    try:
        qdict = { str(i+1) : qlist[i] for i in range(0, len(qlist) ) }
        for k,v in qdict.items():
            qstring+= f"{k}) {v}\n"
    except Exception as error:
        import traceback
        tb = traceback.extract_tb(sys.exc_info()[2], limit=1)[0]
        raise QuestionExceptions(f"{tb} : {str(error)}")

    # Wait for the user input
    while True:
        answer = None
        user_input = input(qstring)
        if user_input in qdict.keys():
            print(f"Selected...{qdict[user_input]}")
            answer = qdict[user_input]
            return answer
        else:
            print(f"\n{user_input} is not a choice.....please choose again\n")
            continue 

def ask_text_input(qstring:str):
    answer = None
    question = qstring + "? "
    answer = input(question)
    return answer.replace(" ", "_").lower()