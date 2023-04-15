"""
CS 4395.002 Human Language Technologies
Dr. Mazidi

Chatbot
Jordan Frimpter JEF 180001
Henry Kim HTK180000
Due: Apr. 15, 2023

This file provides functions for rules-based component of the chatbot.
"""

from nltk.tokenize import word_tokenize

# list of commands that are forbidden without name being known
forbidden_actions = ["FUNC_TOPIC", "FUNC_PAPER_AUTHOR", "FUNC_PAPER_OR_AUTHOR"]
# all function codes
functions = ["FUNC_NAME", "FUNC_EXIT", "FUNC_NONE", "FUNC_DEMAND_NAME", "FUNC_TOPIC", "FUNC_PAPER_AUTHOR",
             "FUNC_PAPER_OR_AUTHOR", "FUNC_HELP"]
# all token codes
tokens = ["TOKEN_YES", "TOKEN_NO", "TOKEN_NAME", "TOKEN_AUTHOR", "TOKEN_COAUTHOR", "TOKEN_PAPER", "TOKEN_HELP",
          "TOKEN_ABSTRACT", "TOKEN_FILEPATH", "TOKEN_TOPIC", "TOKEN_DATE"]


# function counts how many elements from a1 are in a2, not including duplicates
def common_elements(arr1, arr2) -> int:
    """
    Function counts the common elements between two iterables
    :param arr1: iterable element 1
    :param arr2: iterable element 2
    :return: cardinality of set of items appearing in both iterable groups (including duplicates)
    """
    count = 0
    for element in arr1:
        if element in arr2:
            count += 1

    return count


def seek(in_text: str) -> list[str]:
    """
    Tests an input string and parses for tokens and function intentions.
    :param in_text: text to be screened for tokens and functions
    :return: list of strings describing tokens and function codes found
    """

    # tokenize input with lowercase
    in_lower = in_text.lower()
    in_text = word_tokenize(in_lower)

    returnset = []

    # testing for keywords-----------------------------

    # yes testing
    if common_elements(["yes", "yea", "yeah", "yep"], in_text) > 0:
        returnset.append("TOKEN_YES")

    # no testing
    if common_elements(["no", "nah", "nope"], in_text) > 0:
        returnset.append("TOKEN_NO")

    # name token testing
    if common_elements(["name", "names", "identity", "moniker"], in_text) > 0:
        returnset.append("TOKEN_NAME")

    # coauthor testing
    if common_elements(["coauthor", "coauthors", "coauthored", "co-author",
                        "co-authors", "co-authored"], in_text) > 0:
        returnset.append("TOKEN_COAUTHOR")

    # author testing
    if "TOKEN_COAUTHOR" in returnset or common_elements(["author", "authors", "authored", "wrote"], in_text) > 0:
        returnset.append("TOKEN_AUTHOR")

    # paper testing
    if common_elements(["article", "articles", "journal", "journals", "paper", "papers"], in_text) > 0:
        returnset.append("TOKEN_PAPER")

    # help testing
    if common_elements(["help", "helpful", "lost", "helping"], in_text) > 0:
        returnset.append("TOKEN_HELP")

    # abstract testing
    if common_elements(["abstract", "summary", "summarize", "generalize", "subject"], in_text) > 0 or common_elements(
            ["about", "is"], in_text) > 1:
        returnset.append("TOKEN_ABSTRACT")

    # filepath
    if common_elements(["file", "files", "filepath", "path", "paths", "location", "where", "find"], in_text) > 0:
        returnset.append("TOKEN_FILEPATH")

    # topic
    if common_elements(["topic", "subject", "interest", "talk", "discuss"], in_text) > 0:
        returnset.append("TOKEN_TOPIC")

    # date
    if common_elements(["date", "when", "time", "day", "year", "month", "old", "young"], in_text) > 0:
        returnset.append("TOKEN_DATE")

    # testing for phrases-----------------------------

    # name testing: name token and possessive
    if "TOKEN_NAME" in returnset and common_elements(["my", "I", "I'm", "me", "mine"], in_text) > 0:
        returnset.append("FUNC_NAME")

    # pick topic testing
    if "TOKEN_TOPIC" in returnset \
            and common_elements(["pick", "change", "other", "about", "else"], in_text) > 0:
        returnset.append("FUNC_TOPIC")

    # exit testing
    if common_elements(["goodbye", "bye"], in_text) > 0 or common_elements(["i", "have", "to", "go"], in_text) > 3:
        returnset.append("FUNC_EXIT")

    # paper author testing
    if "TOKEN_PAPER" in returnset and "TOKEN_AUTHOR" in returnset:
        returnset.append("FUNC_PAPER_AUTHOR")

    # paper author testing
    if "TOKEN_PAPER" in returnset or "TOKEN_AUTHOR" in returnset:
        returnset.append("FUNC_PAPER_OR_AUTHOR")

    # help seek function
    if "TOKEN_HELP" in returnset and len(returnset) == 1:
        returnset.append("FUNC_HELP")

    # no task found
    if common_elements(functions, returnset) == 0:
        returnset.append("FUNC_NONE")

    return returnset


def seek_simple(in_text: str) -> list[str]:
    """
    Simplified version of seek function used to force name demand function when forbidden actions are requested
    :param in_text: text to be screened for tokens and functions
    :return: list of strings describing tokens and function codes found
    """

    # parse tokens
    response = seek(in_text)

    # if the code is locked, return name demand
    for code in response:
        if code in forbidden_actions:
            return ["FUNC_DEMAND_NAME"]

    # return token set if no illegal functions requested
    return response
