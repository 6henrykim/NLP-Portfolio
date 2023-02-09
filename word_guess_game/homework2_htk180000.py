"""
CS 4395.002 Human Language Technologies
Dr. Mazidi

Homework 2 Word Guess Game
Henry Kim HTK180000
Due: Feb. 18, 2023

This program reads in a file and analyzes it. It then plays a guessing game based on the text read.
A path to the file to read is given as an argument.
"""

import sys
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from random import seed
from random import randint


def guessing_game(word_list):
    """
    Prompts the user to guess the letters in a random word from the word_list. The user starts with 5 points, gains 1
    point for each correctly guessed letter, and loses 1 point for each incorrectly guess. The game ends when the user
    has a negative score or when they enter an !

    :return: final score
    """

    # TODO: Use time as the random seed
    # randomly choose a word
    seed(1)
    target_word = word_list[randint(0, len(word_list))]
    print(target_word)


# Main execution
if __name__ == '__main__':
    # Read filepath from sysarg
    if len(sys.argv) < 2:
        # Error if no filepath given
        print('Error: Please enter a filepath as a system arg')
        sys.exit()

    # TODO: Process the file

    guessing_game(['cat', 'dog'])

