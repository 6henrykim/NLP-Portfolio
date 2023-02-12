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
from nltk.tokenize import word_tokenize
from random import seed
from random import randint
from time import time
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# Download nltk data
# nltk.download()

def lexical_diversity(text):
    """
    Calculates and prints the lexical diversity of the text
    :param text: the text sample to analyze
    """
    tokens = word_tokenize(text)

    # lowercase, get rid of punctuation, numbers
    tokens = [t.lower() for t in tokens if t.isalpha()]
    unique_tokens = set(tokens)

    # Display lexical diversity as the number of unique tokens divided by number of total tokens
    print("Lexical diversity: %.2f" % (len(unique_tokens) / len(tokens)))


def process_text(text):
    """
    Tokenizes the text and removes words in the NLTK stopword list and have length less than or equal to 5
    :return: A list of tokens (not unique) and a list of nouns
    """
    tokens = word_tokenize(text)
    # Lowercase, get rid of punctuation, numbers
    tokens = [t.lower() for t in tokens if (t.isalpha()) and (t not in stopwords.words('english')) and (len(t) > 5)]

    # Get the lemmas
    wnl = WordNetLemmatizer()
    lemmas = [wnl.lemmatize(t) for t in tokens]
    # Make list of unique lemmas
    lemmas_unique = list(set(lemmas))

    # Tag the parts of speech
    tags = nltk.pos_tag(lemmas_unique)
    print("First 20 tagged words:", tags[:20])

    # Make a list of nouns from unique lemmas that have NN in their tag
    nouns = [t[0] for t in tags if "NN" in t[1]]

    print("Number of tokens after preprocessing:", len(tokens))
    print("Number of tokens after preprocessing:", len(nouns))
    return tokens, nouns


def noun_occurrences(tokens, nouns):
    """
    Counts the number of times each noun occurs in a list of tokens
    :param tokens: a list of tokens
    :param nouns: a list of unique nouns
    :return: a dictionary with a noun as the key and its number of occurrences as its value
    """

    # Create the dictionary
    noun_dict = {}
    for noun in nouns:
        noun_dict[noun] = tokens.count(noun)

    # Sort by number of occurrences
    sorted_dict = {key: val for key, val in sorted(noun_dict.items(), key=lambda entry: entry[1], reverse=True)}

    return sorted_dict


def validate_guess(guess):
    """
    Checks if the guess is a single letter or ! and recursively prompts the user again if it is not
    :param guess: input from the user
    :return: a single char that is a letter or !
    """
    guess = guess.lower()
    if (len(guess) == 1 and guess.isalpha()) or guess == '!':
        return guess
    else:
        print("Error: please guess only a single letter")
        new_guess = input("Guess a letter: ").lower()
        return validate_guess(new_guess)


def choose_word(word_list):
    """
    Randomly choose a word from the given list
    :param word_list: a list of word strings to choose from
    :return: a random word string in the list
    """
    seed(time())
    return word_list[randint(0, len(word_list) - 1)]


def display_word(word, guesses):
    """
    Prints letters of a word that have been guessed and underscores for the letters that haven't been guessed yet.
    :param word: the word the user is trying to guess
    :param guesses: a list of characters the user has guessed
    """
    progress = ""
    for letter in word:
        if letter in guesses:
            progress += letter + " "
        else:
            progress += "_ "
    print(progress)


def guessing_game(word_list):
    """
    Prompts the user to guess the letters in a random word from the word_list. The user starts with 5 points, gains 1
    point for each correctly guessed letter, and loses 1 point for each incorrectly guess. The game ends when the user
    has a negative score or when they enter an !
    """

    print("Let's play a word guessing game!")

    # Set up game loop
    guessed_this_round = []
    score = 5
    target_word = choose_word(word_list)

    # Game loop
    while score >= 0:
        # Display user progress on guessing the word
        display_word(target_word, guessed_this_round)

        # Get the user input
        guess_input = validate_guess(input("Guess a letter: "))

        # End game loop if user entered !
        if guess_input == '!':
            break

        # Make sure user has not tried this guess already for this word
        if guess_input in guessed_this_round:
            # Tell user they already tried this letter and skip this iteration
            print("You already guessed", guess_input, "this round. Try a different letter")
            continue
        else:
            guessed_this_round.append(guess_input)

        # Process whether this new guess is correct or not
        if guess_input in target_word:
            score += 1
            print("Right! Score is", score)
        else:
            score -= 1
            print("Sorry, incorrect. Score is", score)

        # Check if all letters in the word have been guessed
        complete = True
        for letter in target_word:
            if letter not in guessed_this_round:
                # Incomplete if any letter in the target word hasn't been guessed yet
                complete = False

        # Prepare for next round once all letters have been guessed
        if complete:
            print("You solved it!")
            display_word(target_word, guessed_this_round)
            print()
            print("current score:", score)
            print()
            print("Guess another word")
            # Reset the target word and list of guesses
            target_word = choose_word(word_list)
            guessed_this_round = []

    # Display the score
    print()
    print("Game over")
    print("Final score:", score)


# Main execution
if __name__ == '__main__':
    # Read filepath from sysarg
    if len(sys.argv) < 2:
        # Error if no filepath given
        print('Error: Please enter a filepath as a system arg')
        sys.exit()

    # Read file into text
    print("Input file:", sys.argv[1])
    with open(sys.argv[1], 'r') as file:
        text = file.read()
    # Remove newline characters
    text = text.replace('\n', ' ')

    # Display the lexical diversity
    lexical_diversity(text)
    print()

    # Process the text
    tokens, nouns = process_text(text)
    print()

    # Get the dictionary of nouns and their number of occurrences
    noun_dict = noun_occurrences(tokens, nouns)

    # Print 50 most common nouns
    most_common_nouns = list(noun_dict.items())[:50]
    print("50 Most common nouns")
    for entry in most_common_nouns:
        print(entry)
    print()

    # Play the guessing game
    game_words = [entry[0] for entry in most_common_nouns]
    guessing_game(game_words)
