"""
CS 4395.002 Human Language Technologies
Dr. Mazidi

Web Crawler
Jordan Frimpter JEF 180001
Henry Kim HTK180000
Due: Mar. 11, 2023

This web crawler collects and saves information from webpages about the Titanic in a database file.
"""

import pickle
import sqlite3
from bs4 import BeautifulSoup
import re
import requests
from urllib import request
import nltk
from nltk import sent_tokenize
from nltk import word_tokenize

# dictionary for robot files
ROBOTS_FILES = {}
# banned urls (common and useless)
BANNED_BASE_URL = ['facebook.com']
# dictionary file
DICT_FILE = "filemap.pickle"
# query robots.txt
CHECK_ROBOT = False


# function to check if a keyword exists in a string
def contains_keywords(text: str, keyword_set: list[str]) -> bool:
    """
    Returns True if the text contains at least one of the keywords
    :param text: text to investigate for keywords
    :param keyword_set: list of string keywords
    :return: A boolean representing whether a keyword was found (true) or not (false)
    """
    # reject incorrect parameters
    if (not isinstance(text, str)) or (not isinstance(keyword_set, list)):
        print("WARNING: invalid datatype given to function contains_keywords")
        return False

    # investigate for keywords
    for key in keyword_set:
        # reject invalid keyword type
        if not isinstance(key, str):
            print("WARNING: invalid datatype in list parameter given to function contains_keywords")
            return False
        # perform check for keyword in string
        if text and key in text.lower():
            return True
    return False


# function for human approval of robots.txt
def approve_scrape(url: str) -> bool:
    """
    Presents robots.txt file for manual inspection and approval/denial based on robots.txt policy
    :param url: string of URL to inspect
    :return: True or False for 'proceed with scrape'
    """

    # parameter validation
    if not isinstance(url, str):
        print("url given to approve_scrape is not a string")
        return False

    # match ID to regex for url base
    match = re.search("^(https?://[^/]+)/.*$", url)

    # if that match failed, try again with root url pattern
    if not match:
        match = re.search("^(https?://[^/]+)$", url)

    # if there is not a match to the regex, reject
    if not match:
        print("REGEX parse failed for url '", url, "'")
        return False

    # collect url base
    url_base = match.group(1)

    # if robots.txt file not in collection, go collect it
    if url_base not in ROBOTS_FILES:
        r = requests.get(url_base + "/robots.txt")
        ROBOTS_FILES[url_base] = r.text
    else:
        print("robots.txt file retrieved from search history collection.")

    # request user approval (print display)
    separate = "======================================"
    print(separate)
    print(ROBOTS_FILES[url_base])
    print(separate)
    print("robots.txt for url \"", url_base, "\"")
    print("base url \"", url, "\"")
    print(separate)

    # loop user approval or denial
    while True:
        user_in = input("Approve? y/n")
        if user_in == "y":
            return True
        if user_in == "n":
            return False
        print("Input '{0}' not recognized".format(user_in))


# function to determine if a URL is in a list of banned URLs
def is_not_banned_url(url: str, silent: bool = False) -> bool:
    """
    resolves whether an url is a banned url, uses banned URL list at the top of the file
    :param url: string of url
    :param silent: boolean for whether it should print rejections
    :return: True or False representing if the url is valid and within the banned base url list
    """
    # if url is not a string, reject
    if (not isinstance(url, str)) or (not isinstance(silent, bool)):
        if not silent:
            print("Rejected parameter type to is_not_banned_url function.")
        return False

    # match ID to regex for url base
    match = re.search("^https?:(//[^/]+)/.*$", url)

    # if that match failed, try again with root url pattern
    if not match:
        match = re.search("^https?:(//[^/]+)$", url)

    # if there is not a match to the regex, reject
    if not match:
        if not silent:
            print("Rejected URL: No base address found for {0}".format(url))
        return False

    # extract base url
    base_url = match.group(1)

    # if base url has been denied, then reject. Otherwise approve
    if base_url in BANNED_BASE_URL:
        if not silent:
            print("Rejected URL: {0}".format(url))
        return False
    return True


# scrape a webpage for urls
def gather_urls(starting_url: str, keyword_list: list[str], filters: list[str], validate: bool = True) -> list[str]:
    """
    Scrapes a webpage for the URLs
    :param starting_url: The starting page to collect URLs from
    :param keyword_list: A list of words that relevant URLs should have
    :param filters: A list of words that relevant URLs should not have
    :param validate: (default True) a boolean to determine whether to perform type-checking
    :return: A list of URLs related to the starting topic
    """

    # reject invalid parameters ===================
    # if validate is a bool and is true, validate all the other parameters as well
    if isinstance(validate, bool):
        if validate:
            if not isinstance(starting_url, str):
                print("WARNING: nonstring value given to gather_url as argument 0")
                return []
            if not isinstance(keyword_list, list):
                print("WARNING: non-list value given to gather_url as argument 1")
                return []
            if not isinstance(filters, list):
                print("WARNING: non-list value given to gather_url as argument 2")
                return []
            for item in keyword_list:
                if not isinstance(item, str):
                    print("WARNING: non-string value given to list of gather_url argument 1")
                    return []
            for item in filters:
                if not isinstance(item, str):
                    print("WARNING: non-string value given to list of gather_url argument 2")
                    return []
    else:
        print("WARNING: non-bool value given to gather_url's as validation boolean")
        return []

    # function ===================

    # Request the page and store it as a soup object
    r = requests.get(starting_url)
    data = r.text
    soup = BeautifulSoup(data, features='html.parser')

    # Collect URLs and write to a file
    url_list = []
    for link in soup.find_all('a'):
        url = link.get('href')
        url_list.append(url)

    # Get the unique URLs
    url_list = list(set(url_list))

    # Only save urls that have one of the keywords
    if len(keyword_list) > 0:
        url_list = [url for url in url_list if contains_keywords(url, keyword_list)]

    # filter out banned base urls
    url_list = [url for url in url_list if is_not_banned_url(url, False)]

    # Remove urls that have filtered words
    if len(filters) > 0:
        url_list = [url for url in url_list if not contains_keywords(url, filters)]

    # Write the urls to file and print them
    print('URLs gathered')
    with open('urls.txt', 'w') as f:
        for unique_url in url_list:
            print(unique_url)
            f.write(str(unique_url) + '\n')

    # Return the URLs
    return url_list


# scrape a webpage for text
def scrape_raw_text(target_url: str, out_filename: str) -> str:
    """
    Scrapes the raw paragraph text from a given URL and stores it in a file
    :param target_url: The URL to scrape from
    :param out_filename: The file to save the raw text to
    :return: The raw text scraped
    """

    # reject invalid parameters
    if (not isinstance(target_url, str)) or (not isinstance(out_filename, str)):
        print("WARNING: Invalid arguments to scrape_raw_text")
        return "NONE"

    # if 'consult robots.txt' is enabled and the webpage was not approved, reject
    if CHECK_ROBOT:
        if not approve_scrape(target_url):
            return "NONE"

    # fetch page information
    try:
        html = request.urlopen(target_url).read().decode('utf8')
    except:
        print('Error requesting ' + target_url)
        raise Exception('Request error')

    soup = BeautifulSoup(html, features='html.parser')

    # Rip out all script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    paragraphs = soup.select('p')
    p_text = [p.text for p in paragraphs]
    raw_text = '\n'.join(p_text)

    # Write the raw text to a file
    with open(out_filename, 'w', encoding='utf-8') as f:
        # Write the URL as the first line
        f.write(target_url + '\n')
        # Write the rest of the text
        f.write(raw_text)

    return raw_text


# scrub a text file
def clean_text(in_filename: str, out_filename: str):
    """
    Cleans the text in the input file and stores its sentences in the output file
    DOES NOT validate that the file actually exists
    :param in_filename: file to read from
    :param out_filename: file to write to
    :return:
    """

    # validate parameter data types
    if (not isinstance(in_filename, str)) or (not isinstance(out_filename, str)):
        print("WARNING: Invalid parameter type to clean_text")
        return

    # open file
    with open(in_filename, 'r', encoding='utf-8') as f:
        # The first line is the URL
        url = f.readline()
        # Read the rest of the lines
        raw_lines = f.readlines()

    # Filter out lines that are just white space
    raw_lines = [line.strip() for line in raw_lines if not re.match(r'^\s*$', line)]

    cleaned_text = ' '.join(raw_lines)
    sentences = sent_tokenize(cleaned_text)

    # write to file
    with open(out_filename, 'w', encoding='utf-8') as f:
        # The first line is the URL
        f.write(url + '\n')
        # Write the rest of the lines
        for sentence in sentences:
            f.write(sentence + '\n')
            # print(sentence)


# function for gathering info from websites
def scrape_and_clean(url_list: list[str]) -> dict[str, (str, str)]:
    """
    Scrapes raw text from the url_list and cleans it into sentences
    :param url_list: A list of URLs to scrape
    :return: A dictionary of filenames keyed by their source URL
    """
    # Key: a URL string
    # Value: a tuple (raw_filename, clean_filename)
    file_dict = {}

    # validate parameters
    if not isinstance(url_list, list):
        print("WARNING: invalid parameter to scrape_and_clean")
        return file_dict

    # Scrape the data and tokenize into sentences
    i = 0
    for url in url_list:
        if not isinstance(url, str):
            print("WARNING: invalid URL found in URL list; skipped")
            continue

        raw_filename = 'raw_text_' + str(i) + '.txt'
        clean_filename = 'sentences_' + str(i) + '.txt'

        # Skip adding to dictionary if there was an error
        try:
            # if the file was rejected for scraping, don't iterate i or save the file to the collection
            if scrape_raw_text(url, raw_filename) == "NONE":
                print("FILE rejected for {}.".format(url))
                continue
            clean_text(raw_filename, clean_filename)
        except:
            continue

        file_dict[url] = (raw_filename, clean_filename)
        i += 1

    return file_dict


def tf_ids(filename_list: list[str]) -> list:
    """
    Counts the most common terms since tf-idf is good for identifying relevant terms to specific document
    compared to other documents, but we want the overall most relevant terms for all documents
    :param filename_list: list of filenames to inspect
    :return: returns a list of the sorted keywords, sorted by tf-ids metric
    """
    stopwords = nltk.corpus.stopwords.words('english')
    dict_of_dict = {}

    # open and read files
    for filename in filename_list:
        # open dictionary
        occurrences_dict = {}

        # open file
        with open(filename, 'r', encoding='utf-8') as f:
            # The first line is the URL
            _ = f.readline()
            # Read the rest of the lines
            text = f.read().lower().replace('\n', ' ')

        # read tokens, tokenize, and count in dictionary
        tokens = word_tokenize(text)
        tokens = [t for t in tokens if t.isalpha() and t not in stopwords]
        for t in tokens:
            if t in occurrences_dict:
                occurrences_dict[t] += 1
            else:
                occurrences_dict[t] = 1

        # stash dictionary in dict of dicts
        dict_of_dict[filename] = occurrences_dict

    # generate term frequency
    if_dict_dict = {}
    for filename in dict_of_dict:
        # collect total tokens in doc
        total = 0
        for word in dict_of_dict[filename]:
            total += dict_of_dict[filename][word]
        # generate term frequency per document
        if_dict = {}
        for word in dict_of_dict[filename]:
            if_dict[word] = dict_of_dict[filename][word] / total
        if_dict_dict[filename] = if_dict

    # generate term frequency totals per word
    if_total_dict = {}
    for filename in if_dict_dict:
        for word in if_dict_dict[filename]:
            if word in if_total_dict:
                if_total_dict[word] += if_dict_dict[filename][word]
            else:
                if_total_dict[word] = if_dict_dict[filename][word]

    # generate inverse document frequency
    # count the number of documents that has each word in it
    word_doc_count = {}
    for instance in if_dict_dict:
        for word in if_dict_dict[instance]:
            if word in word_doc_count:
                word_doc_count[word] += 1
            else:
                word_doc_count[word] = 1
    # generate the IDF for each word
    doc_count = len(if_dict_dict)
    idf = {}
    for word in word_doc_count:
        idf[word] = doc_count / word_doc_count[word]

    # calculate if-ids
    if_ids_dict = {}
    for word in idf:
        if_ids_dict[word] = idf[word] * if_total_dict[word]

    occurrences = sorted(if_ids_dict.items(), key=lambda x: x[1], reverse=True)
    for i, occurrence in enumerate(occurrences[:25]):
        print(str(i + 1) + ': ' + str(occurrence))

    return [occurrence[0] for occurrence in occurrences]


def scrape(url: str, filter_pos: list[str], filter_neg: list[str]):
    """
    Scrapes one page deep for all URLs in a given starting position
    :param url: string representing starting URL
    :param filter_pos: list of strings representing words a URL must possess
    :param filter_neg: list of strings representing words a URL may not possess
    :return: a dictionary mapping urls to raw text files (raw text, clean text)
    file_clean is a dictionary mapping urls to cleaned text files
    """

    # return value dictionaries
    file_dict = {}

    # reject invalid parameters======================
    # reject wrong type entities
    if not isinstance(url, str) or not isinstance(filter_pos, list) or not isinstance(filter_neg, list):
        print("invalid arguments given to function scrape.")
        return file_dict

    # reject filter_pos if nonstring entities
    for item in filter_pos:
        if not isinstance(item, str):
            print("invalid arguments given to function scrape (list element of positive filter not str).")
            return file_dict

    # reject filter_neg if nonstring entities
    for item in filter_neg:
        if not isinstance(item, str):
            print("invalid arguments given to function scrape (list element of negative filter not str).")
            return file_dict

    # function begin======================
    # Scrape a list of URLs from the starting URL
    urls = gather_urls(start_url, filter_pos, filter_neg)

    # Put the starting URL into the list of pages to scrape for content
    urls.append(start_url)

    # scrape web content
    file_dict = scrape_and_clean(urls)

    # For testing without doing all scraping
    # filenames = ['sentences_' + str(i) + '.txt' for i in range(0,5)]

    # pickle the dictionary
    with open(DICT_FILE, 'wb') as output:
        pickle.dump(file_dict, output)

    return file_dict


def most_frequent_terms(files: list[str]) -> list:
    """
    Counts the number of times each word occurs in the corpus and prints the most frequent ones
    :param files: A list of filenames
    :return: a list of frequent terms
    """
    stopwords = nltk.corpus.stopwords.words('english')
    occurrences_dict = {}

    # open and read files
    for instance in files:
        with open(instance, 'r', encoding='utf-8') as f:
            # The first line is the URL
            _ = f.readline()
            # Read the rest of the lines
            text = f.read().lower().replace('\n', ' ')

        # read tokens, tokenize, and count in dictionary
        tokens = word_tokenize(text)
        tokens = [t for t in tokens if t.isalpha() and t not in stopwords]
        for t in tokens:
            if t in occurrences_dict:
                occurrences_dict[t] += 1
            else:
                occurrences_dict[t] = 1

    occurrences = sorted(occurrences_dict.items(), key=lambda x: x[1], reverse=True)
    print('Most frequent words by count')
    for i, word in enumerate(occurrences[:25]):
        print(str(i + 1) + ': ' + str(word))

    return [occurrence[0] for occurrence in occurrences]


def create_database(db_name: str, files: list[str], keyword_list: list[str]):
    """
    Creates an SQLite database of sentences and
    :param db_name: Name of the database file
    :param files: List of files to search for relevant sentences
    :param keyword_list: List of keywords that identify relevant sentences
    :return:
    """
    # Open the database
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    # Enable foreign keys for the tags table
    connection.execute("PRAGMA foreign_keys = 1")

    # Delete old entries
    cursor.execute("DROP TABLE IF EXISTS tags")
    cursor.execute("DROP TABLE IF EXISTS facts")
    connection.commit()

    # Initialize the tables
    cursor.execute("CREATE TABLE IF NOT EXISTS facts ( "
                   "sentence TEXT NOT NULL, "
                   "source TEXT, "
                   "PRIMARY KEY (sentence))")
    cursor.execute("CREATE TABLE IF NOT EXISTS tags ("
                   "sentence TEXT NOT NULL, "
                   "tag TEXT NOT NULL, "
                   "FOREIGN KEY (sentence) REFERENCES facts(sentence) ON DELETE CASCADE)")
    connection.commit()

    # Iterate over files
    for file_from_set in files:
        f = open(file_from_set, 'r', encoding='utf-8')
        # The first line is the URL
        url = f.readline()
        # Read the rest of the lines
        lines = f.readlines()
        f.close()

        # Each line has the potential to go into the database, but not all will
        for line in lines:
            # Each keyword in the sentence will be used as a tag in the database
            for keyword in keyword_list:
                if keyword.lower() in line.lower():
                    # Check if this fact is already in database
                    query = cursor.execute("SELECT * FROM facts WHERE sentence=?", (line,)).fetchall()
                    # If fact not in database, add it
                    if not query:
                        cursor.execute("INSERT INTO facts VALUES (?, ?)", (line, url,))
                        connection.commit()
                    # Add the tag
                    cursor.execute("INSERT INTO tags VALUES (?, ?)", (line, keyword))
                    connection.commit()

    # Close the database connection
    cursor.close()
    connection.close()


# Main execution
if __name__ == '__main__':
    print('Web crawler')

    # Starting URL
    start_url = 'https://en.wikipedia.org/wiki/Titanic'
    filter_words_positive = []
    filter_words_negative = ['wikimedia', 'wikipedia']

    # generate file scraped dictionaries
    # recommended to use this as few times as possible to avoid upsetting website hosts
    files_dict = scrape(start_url, filter_words_positive, filter_words_negative)

    # intermediate code: uncomment to load pickle when redesigning database from existing files
    # with open(DICT_FILE, 'rb') as file:
    #    files_dict = pickle.load(file)

    # generate file list
    file_list = [files_dict[file][1] for file in files_dict]

    # process files
    sorted_words = most_frequent_terms(file_list)

    # Top 10 terms picked from most frequent terms
    # keywords = sorted_words[:10]
    keywords = ['titanic',
                'ship',
                'maritime',
                'salvage',
                'wreck',
                'bodies',
                'dead',
                'iceberg',
                'sea',
                'steel']

    # Create database
    create_database('database.db', file_list, keywords)
