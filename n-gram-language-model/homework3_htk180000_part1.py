"""
CS 4395.002 Human Language Technologies
Dr. Mazidi

Homework 3 N-Gram Language Model
Henry Kim HTK180000
Due: Mar. 4, 2023

Part 1
This program reads in files and outputs pickled dictionaries that counts the unigrams and bigrams in them.
"""

from nltk import word_tokenize
from nltk.util import ngrams
import pickle


def count_unigrams_and_bigrams(filepath):
    """
    Counts the number of times each unigram and bigram in the specified file.
    :param filepath: The path to the training file to count unigrams and bigrams in.
    :return: A dictionary of unigrams with their number of occurrences and a dictionary of bigrams with their number
    of occurrences.
    """
    # Read file into text
    with open(filepath, 'r', encoding='utf8') as file:
        text = file.read()

    # Remove newline characters and lowercase the text
    text = text.replace('\n', ' ')
    text = text.lower()

    # Get list of unigrams
    unigrams = [t.lower() for t in word_tokenize(text)]
    # Replace the numbers with NUM since numbers aren't likely to reveal which language text is
    unigrams = ['NUM' if u.isdigit() else u for u in unigrams]

    # Count the unigrams
    unigram_dict = {u: unigrams.count(u) for u in set(unigrams)}

    # Get list of unigrams
    bigrams = list(ngrams(unigrams, 2))
    # Count the bigrams
    bigram_dict = {b: bigrams.count(b) for b in set(bigrams)}

    # Return the dictionaries
    return unigram_dict, bigram_dict


# Main execution
if __name__ == '__main__':
    training_data = ['LangId.train.English', 'LangId.train.French', 'LangId.train.Italian']

    # Process each of the files
    for filename in training_data:
        print('Input file:', filename)
        unigram_count, bigram_count = count_unigrams_and_bigrams(filename)

        # Save the unigram dictionary as a pickle file
        output_filename = filename + '.unigrams.pickle'
        print('Output file:', output_filename)
        print(unigram_count)
        with open(output_filename, 'wb') as output:
            pickle.dump(unigram_count, output)

        # Save the bigram dictionary as a pickle file
        output_filename = filename + '.bigrams.pickle'
        print('Output file:', output_filename)
        print(bigram_count)
        with open(output_filename, 'wb') as output:
            pickle.dump(bigram_count, output)
