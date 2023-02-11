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


def validate_guess(guess):
    """
    Checks if the guess is a single letter or ! and recursivelhy prompts the user again if it is not
    :param guess: input from the user
    :return: a single char
    """
    if (len(guess) == 1 and guess.isalpha()) or guess == '!':
        return guess
    else:
        print("Error: please guess only a single letter")
        new_guess = input("Guess a letter: ").lower()
        return validate_guess(new_guess)



def guessing_game(word_list):
    """
    Prompts the user to guess the letters in a random word from the word_list. The user starts with 5 points, gains 1
    point for each correctly guessed letter, and loses 1 point for each incorrectly guess. The game ends when the user
    has a negative score or when they enter an !

    :return: final score
    """
    score = 5

    # Randomly choose a word
    # TODO: Use time as the random seed
    seed(1)
    target_word = word_list[randint(0, len(word_list))]
    print(target_word)

    # Game loop
    keep_playing = True
    guesses_this_round = {}

    while keep_playing:
        # TODO: print the underscores

        letter_guess = input("Guess a letter: ").lower()
        letter_guess = validate_guess(letter_guess)
        if letter_guess == '!':
            keep_playing = False
        else:
            # Check answer, adjust score
            # Get the next word


    # Return the score
    return score


# Main execution
if __name__ == '__main__':
    # Read filepath from sysarg
    if len(sys.argv) < 2:
        # Error if no filepath given
        print('Error: Please enter a filepath as a system arg')
        sys.exit()

    # TODO: Process the file

    # Play the guessing game
    print("Let's play a word guessing game!")
    final_score = guessing_game(['cat', 'dog'])
    print()
    print("Final score:", final_score)

