"""
CS 4395.002 Human Language Technologies
Dr. Mazidi

Chatbot
Jordan Frimpter JEF 180001
Henry Kim HTK180000
Due: Apr. 15, 2023

This file provides functions for parsing user input.
"""

import jef180001_htk180000_baxter as bax
from nltk.tokenize import word_tokenize
import spacy

# named entity recognition
NER = spacy.load("en_core_web_sm")

def parse_proper_noun(in_text: str) -> str:
    """
    parse proper noun (single) from a string
    :param in_text: text to parse
    :return: single string of space-concatenated proper nouns
    """
    tag_text = NER(in_text)  # label tokens in input

    name_candidate = ""  # generate candidate name

    for element in tag_text:  # concatenate named entities
        if element.pos_ == "PROPN":  # if proper noun, add
            name_candidate += element.text + " "

    name_candidate = name_candidate[:-1]  # crop off space

    return name_candidate


def pair_tokens(in_text: str, tuple_array: list):
    """
    Calculate token similarity metric between a string and a set of tuples containing strings
    :param in_text: input text
    :param tuple_array: list of tuples whose first element is a string
    :return: tuple whose first element matches most closely in terms of token counts
    """
    # tokenize input
    tokens = in_text.lower()
    tokens = word_tokenize(tokens)

    # tuple rank [count of similarity]
    tuple_rank = [0] * len(tuple_array)

    # check for a match in the tuples [count every time a word appears in a tuple's title]
    for token in tokens:
        for i in range(len(tuple_array)):
            # tokenize the first element of the tuple being tested
            words = tuple_array[i][0]
            words = words.lower()
            words = word_tokenize(words)
            # calculate if current token tested was in the tokenized element of the tuple
            for word in words:
                if token == word:
                    tuple_rank[i] += 1

    # find largest ranked tupple
    greatest_val = 0
    greatest_index = 0
    for i in range(len(tuple_rank)):
        if tuple_rank[i] > greatest_val:
            greatest_index = i
            greatest_val = tuple_rank[i]

    # if there was no largest, return nothing
    if greatest_val == 0:
        return ""
    # return greatest
    return tuple_array[greatest_index]


# loop for user input
def validation_loop() -> str:
    """
    Loops until user gives a satisfactory text answer and approves the text.
    :return: string of approved user-input text
    """

    #retrieve text from user
    in_text = input()

    # while the user has not confirmed the text, keep getting new text
    while True:
        # test if user approves input
        print("You have said '{}'. Is this correct?".format(in_text))
        confirm = input()
        baxter_response = bax.seek(confirm)
        # if confirmed, return text
        if "TOKEN_YES" in baxter_response:
            return in_text
        # if not confirmed, recieve more input
        print("Please type more specifically for me. Tell me again.")
        in_text = input()


# creates a list display for the tuples
def list_display(tuple_array: list) -> str:
    """
    Generates a list display for a set of tuples whose first element should be displayed
    :param tuple_array: list of tuples whose first element should be printed in a list
    :return: string visually representing a list
    """
    out = ""
    i = 1
    for author in tuple_array:
        out += str(i) + ". " + author[0] + "\n"
        i += 1
    return out


# splits a long line into a paragraph display chunk
def line_segment(in_text: str, count: int) ->str:
    """
    Breaks input text to have n space-seperated tokens per line.
    :param in_text: string of input text
    :param count:  per line
    :return: string of text reformatted to have n tokens per line
    """
    tokens = in_text.split(" ")
    i = 1
    out = ""
    sub_out = ""
    # generate lines of tokens
    for token in tokens:
        sub_out += token + " "
        i += 1
        # concatenate as new line at the nth token
        if i >= count:
            out += "\n" + sub_out
            sub_out = ""
            i = 1
    # concatenate leftovers
    out += "\n" + sub_out
    return out
