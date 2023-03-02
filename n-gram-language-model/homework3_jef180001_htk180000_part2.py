"""
CS 4395.002 Human Language Technologies
Dr. Mazidi

Homework 3 N-Gram Language Model
Jordan Frimpter
Henry Kim
Due: Mar. 4, 2023

Part 2
This program uses unigram and bigram occurrences counted in part 1 to calculate the probabilities a string came from
one of the languages.
"""

from nltk import word_tokenize
from nltk.util import ngrams
import pickle
import math


def compute_log_prob(text: str, unigram_dict: dict[str, int], bigram_dict: dict[str, int], vocab_size: int):
    """
    Computes the probability of generating the text from a language given a dictionary of unigram and bigram occurrences
    using Laplace smoothing to compensate for tokens not seen in training.
    :param text: The text to calculate probability of.
    :param unigram_dict: The dictionary of unigram occurrences
    :param bigram_dict: The dictionary of bigram occurrences
    :param vocab_size: The total number of unique words in all training dictionaries
    :return: The probability of generating the text from the training data
    """

    # Remove newline characters and lowercase the text
    text = text.replace('\n', ' ')
    text = text.lower()

    # unigram generation
    unigrams_test = [t.lower() for t in word_tokenize(text)]  # lowercase to consistency
    # Replace the numbers with NUM since numbers aren't likely to reveal which language text is
    unigrams_test = ['NUM' if u.isdigit() else u for u in unigrams_test]

    # bigram generation
    bigrams_test = list(ngrams(unigrams_test, 2))  # generate list of bigrams in test text

    p_laplace = 1
    # generate probabilities for all the following words
    for bigram in bigrams_test:

        # get bigram count from training
        bigram_occurrences = bigram_dict[bigram] if bigram in bigram_dict else 0

        # get unigram count from training
        unigram = bigram[0]
        unigram_occurrences = unigram_dict[unigram] if unigram in unigram_dict else 0

        # calculate log probability
        p_laplace += math.log((bigram_occurrences + 1 / (unigram_occurrences + vocab_size)), 2)

    return p_laplace


# Main execution
if __name__ == '__main__':
    # Expects files to exist; failing for files being inaccessible is a suitable catastrophic failure given the scope.

    # Get the dictionaries, the length of training data, and the vocab size from stored pickles
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

    # Calculate total vocab size of the three languages:
    total_vocab_size = len(english_unigrams)
    total_vocab_size += len(french_unigrams)
    total_vocab_size += len(italian_unigrams)

    # Create a dictionary of predictions for each line
    i = 1  # start at 1 used to match indexes with the given file indexes
    predictions = {}
    for line in lines:
        english_log_prog = compute_log_prob(line, english_unigrams, english_bigrams, total_vocab_size)
        french_log_prog = compute_log_prob(line, french_unigrams, french_bigrams, total_vocab_size)
        italian_log_prog = compute_log_prob(line, italian_unigrams, italian_bigrams, total_vocab_size)

        # select greatest prediction as the prediction to save to the dictionary
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
    i = 1  # start at 1 used to match indexes with the given file indexes
    num_wrong = 0
    print('Missed predictions:')
    for line in lines:
        actual = line.split()[1]
        if actual != predictions[i]:
            print(str(i) + '\t\tActual: ' + actual + '\t\tPredicted: ' + predictions[i])
            num_wrong += 1
        i += 1

    # output special message for all correct
    if num_wrong == 0:
        print("[no predictions were misclassifications]")

    # Output accuracy
    print('Total accuracy: ' + str(1 - (num_wrong / i)))
