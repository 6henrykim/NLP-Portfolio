# NLP-Portfolio
This is my portfolio for the CS 4365.001 Human Language Technologies course taught by Dr. Mazidi at UTDallas. These projects were completed for the Spring 2023 semester. 

## Overview of Natural Language Processing
[Here](overview_of_nlp.pdf) are my responses to some prompts about natural language processing.


## Basic Text Processing
This is a basic text processor that takes a data file of employee information and formats it. The employee data is also saved as a pickle file. The code for the project can be viewed [here](text_processing/homework1_htk180000.py).

### How To Run
Use Python3 to run the homework1_htk180000.py file in the text_processing folder and provide a path to the data file. For example:

> python homework1_htk180000.py data/data.csv

The data file should contain entries where each line is 

> Last,First,Middle Initial,ID,Office phone

with the first line being the headers.

### Reflection
One of the strengths of Python for a text processing task like this is the built-in methods for strings such as title(), lower(), and upper() for easy edits to capitalization. Reading each entry of the data is also fairly simple with the way Python can iterate over all the lines of a file. On the other hand, using classes and objects is not as secure in Python as other langauges due to the lack of access modifiers, which could cause issues for larger projects.

While completing this assignment, I learned about saving objects as pickle files and using regular expressions in Python. Specifically, I found the fullmatch() useful for validating the format of strings. I also reviewed the use of sysargs and taking command line arguments as input for a Python program.


## Word Guess Game
This program takes a text file, calculates its lexical diversity, tokenizes it, and plays a word guessing game based on the most common nouns in the document. The code for the project can be viewed [here](word_guess_game/homework2_htk180000.py).

### How To Run
Use Python3 to run the homework2_htk180000.py file in the word_guess_game folder and provide a path to the data file. For example:

> python homework1_htk180000.py data.txt

Note: this program uses the NLTK library and requires that nltk.download() have already been used to download corpora data.  I used nltk.download('all') to get all available data.


## WordNet
This [Python notebook](wordnet/homework3_htk180000.ipynb) contains an exploration of WordNet's capabilities. There is also a [pdf](wordnet/homework3_htk180000.pdf) version of it.
