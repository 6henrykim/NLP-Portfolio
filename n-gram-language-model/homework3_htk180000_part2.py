"""
CS 4395.002 Human Language Technologies
Dr. Mazidi

Homework 3 N-Gram Language Model
Henry Kim HTK180000
Due: Mar. 4, 2023

Part 2
This program uses unigram and bigram occurrences counted in part 1 to calculate the probabilities a string came from
one of the languages.
"""

from nltk import word_tokenize
from nltk.util import ngrams
import pickle
import math


def compute_log_prob(text, unigram_dict, bigram_dict):
    """
    Computes the log probability of generating the text given a dictionary of unigram and bigram occurrences using
    Laplace smoothing to compensate for tokens not seenin training.
    :param text: The text to calculate probability of.
    :param unigram_dict: The dictionary of unigram occurrences
    :param bigram_dict: The dictionary of bigram occurrences
    :return: The log probability of generating the text from the training data
    """
    # Remove newline characters and lowercase the text
    text = text.replace('\n', ' ')
    text = text.lower()

    unigrams_test = word_tokenize(text)
    bigrams_test = list(ngrams(unigrams_test, 2))
    vocab_size = len(unigram_dict)

    # calculate log probability using Laplace smoothing
    p_log = 0
    for bigram in bigrams_test:
        # n is the number of times the bigram occurs in the training data
        n = bigram_dict[bigram] if bigram in bigram_dict else 0
        # d is the number of times the first word of the bigram occurs in the training data
        d = unigram_dict[bigram[0]] if bigram[0] in unigram_dict else 0

        p_log = p_log + math.log(((n + 1) / (d + vocab_size)))
    return p_log


# Main execution
if __name__ == '__main__':
    # Get the dictionaries, the length of training data, and the vocab size
    with open('LangId.train.English.unigrams.pickle', 'rb') as file:
        english_unigrams = pickle.load(file)
    with open('LangId.train.English.bigrams.pickle', 'rb') as file:
        english_bigrams = pickle.load(file)

    with open('LangId.train.French.unigrams.pickle', 'rb') as file:
        french_unigrams = pickle.load(file)
    with open('LangId.train.French.bigrams.pickle', 'rb') as file:
        french_bigrams = pickle.load(file)

    with open('LangId.train.Italian.unigrams.pickle', 'rb') as file:
        italian_unigrams = pickle.load(file)
    with open('LangId.train.Italian.bigrams.pickle', 'rb') as file:
        italian_bigrams = pickle.load(file)

    # Read in the test file
    with open('LangId.test', 'r', encoding='utf8') as file:
        lines = file.readlines()

    # Create a dictionary of predictions
    i = 1
    predictions = {}
    for line in lines:
        english_log_prog = compute_log_prob(line, english_unigrams, english_bigrams)
        french_log_prog = compute_log_prob(line, french_unigrams, french_bigrams)
        italian_log_prog = compute_log_prob(line, italian_unigrams, italian_bigrams)

        max_log_prog = english_log_prog
        predictions[i] = 'English'

        if french_log_prog > max_log_prog:
            max_log_prog = french_log_prog
            predictions[i] = 'French'

        if italian_log_prog > max_log_prog:
            max_log_prog = italian_log_prog
            predictions[i] = 'Italian'

        i += 1

    # Output predictions to a file
    with open('predictions.txt', 'w') as file:
        for k, v in predictions.items():
            file.write(str(k) + ' ' + v + '\n')

    # Read in the solution file
    with open('LangId.sol', 'r', encoding='utf8') as file:
        lines = file.readlines()

    # Check the answers and calculate answers
    i = 1
    num_wrong = 0
    print('Missed predictions:')
    for line in lines:
        actual = line.split()[1]
        if actual != predictions[i]:
            print(str(i) + '\t\tActual: ' + actual + '\t\tPredicted: ' + predictions[i])
            num_wrong += 1
        i += 1

    # Output accuracy
    print('Total accuracy: ' + str(1 - (num_wrong / i)))
