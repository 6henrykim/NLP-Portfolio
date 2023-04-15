"""
CS 4395.002 Human Language Technologies
Dr. Mazidi

Chatbot
Jordan Frimpter JEF 180001
Henry Kim HTK180000
Due: Apr. 15, 2023

This file provides functions for the database backend of the chatbot
"""

import sqlite3

# Global variables
database_filename = 'database.db'


def create_database():
    """
    Initializes tables in the database if they don't already exist
    """
    try:
        # Open the database
        connection = sqlite3.connect(database_filename)
        cursor = connection.cursor()

        # Enable foreign keys
        connection.execute("PRAGMA foreign_keys = 1")

        # Initialize the entity tables
        cursor.execute("CREATE TABLE IF NOT EXISTS users ("
                       "pk INTEGER PRIMARY KEY,"
                       "name TEXT NOT NULL UNIQUE)")
        cursor.execute("CREATE TABLE IF NOT EXISTS papers ("
                       "pk INTEGER PRIMARY KEY,"
                       "title TEXT NOT NULL UNIQUE, "
                       "abstract TEXT,"
                       "url TEXT,"
                       "filename TEXT UNIQUE)")
        cursor.execute("CREATE TABLE IF NOT EXISTS authors ("
                       "pk INTEGER PRIMARY KEY,"
                       "url TEXT,"
                       "name TEXT NOT NULL UNIQUE)")
        cursor.execute("CREATE TABLE IF NOT EXISTS volumes ("
                       "pk INTEGER PRIMARY KEY,"
                       "url TEXT,"
                       "title TEXT NOT NULL UNIQUE,"
                       "year INTEGER,"
                       "month TEXT)")
        connection.commit()

        # Initialize the relation tables
        cursor.execute("CREATE TABLE IF NOT EXISTS explored_papers ("
                       "user INTEGER NOT NULL,"
                       "paper INTEGER NOT NULL,"
                       "FOREIGN KEY (user) REFERENCES users(pk) ON DELETE CASCADE,"
                       "FOREIGN KEY (paper) REFERENCES papers(pk) ON DELETE CASCADE,"
                       "UNIQUE (user, paper))")
        cursor.execute("CREATE TABLE IF NOT EXISTS explored_authors ("
                       "user INTEGER NOT NULL,"
                       "author INTEGER NOT NULL,"
                       "FOREIGN KEY (user) REFERENCES users(pk) ON DELETE CASCADE,"
                       "FOREIGN KEY (author) REFERENCES authors(pk) ON DELETE CASCADE,"
                       "UNIQUE (user, author))")
        cursor.execute("CREATE TABLE IF NOT EXISTS written_by ("
                       "author INTEGER NOT NULL,"
                       "paper INTEGER NOT NULL,"
                       "FOREIGN KEY (author) REFERENCES authors(pk) ON DELETE CASCADE,"
                       "FOREIGN KEY (paper) REFERENCES papers(pk) ON DELETE CASCADE,"
                       "UNIQUE (author, paper))")
        cursor.execute("CREATE TABLE IF NOT EXISTS coauthors ("
                       "author1 INTEGER NOT NULL,"
                       "author2 INTEGER NOT NULL,"
                       "FOREIGN KEY (author1) REFERENCES authors(pk) ON DELETE CASCADE,"
                       "FOREIGN KEY (author2) REFERENCES authors(pk) ON DELETE CASCADE,"
                       "UNIQUE (author1, author2))")
        cursor.execute("CREATE TABLE IF NOT EXISTS published_in ("
                       "paper INTEGER NOT NULL,"
                       "volume INTEGER NOT NULL,"
                       "FOREIGN KEY (paper) REFERENCES papers(pk) ON DELETE CASCADE,"
                       "FOREIGN KEY (volume) REFERENCES volumes(pk) ON DELETE CASCADE,"
                       "UNIQUE (paper, volume))")
        connection.commit()

        # Close the database connection
        cursor.close()
        connection.close()

    except Exception as e:
        print(e)
        return e


def clear_database():
    """
    Deletes the tables from the database
    """

    try:
        # Open the database
        connection = sqlite3.connect(database_filename)
        cursor = connection.cursor()

        # Delete old relation tables
        cursor.execute("DROP TABLE IF EXISTS explored_papers")
        cursor.execute("DROP TABLE IF EXISTS explored_authors")
        cursor.execute("DROP TABLE IF EXISTS written_by")
        cursor.execute("DROP TABLE IF EXISTS published_in")
        cursor.execute("DROP TABLE IF EXISTS coauthors")
        connection.commit()

        # Delete old entity tables
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS papers")
        cursor.execute("DROP TABLE IF EXISTS authors")
        cursor.execute("DROP TABLE IF EXISTS volumes")
        connection.commit()

        # Close the database connection
        cursor.close()
        connection.close()

    except Exception as e:
        print(e)
        return e


def query_database(command: str, arguments: tuple):
    """
    Executes a single command in the database.
    :param command: The command to execute
    :param arguments: The arguments to use in the command
    """
    try:
        # Open the database
        connection = sqlite3.connect(database_filename)
        cursor = connection.cursor()
        connection.execute("PRAGMA foreign_keys = 1")

        query = cursor.execute(command, arguments)
        result = query.fetchall()
        connection.commit()

        # Close the database connection
        cursor.close()
        connection.close()

        return result

    except Exception as e:
        # TODO: Comment this line out to hide error messages
        # print(e)
        return e


def insert_users_entry(name: str):
    """
    Enters a new user into the database.
    :param name: The name of the user
    """
    query_database("INSERT INTO users (name) VALUES (?)", (name,))


def insert_papers_entry(title: str, abstract: str, filename: str, url: str):
    """
    Enters a paper into the database.
    :param title: The title of the paper
    :param abstract: The abstract of the text
    :param filename: Filename of the file where pdf of the paper is stored
    :param url: URL to webpage of the paper
    """
    query_database("INSERT INTO papers (title, abstract, filename, url) VALUES (?, ?, ?, ?)",
                   (title, abstract, filename, url))


def insert_authors_entry(name: str, url: str):
    """
    Enters a new author into the database.
    :param name: The name of the author
    :param url: URL to the webpage of the author
    """
    query_database("INSERT INTO authors (name, url) VALUES (?, ?)", (name, url))


def insert_volumes_entry(title: str, year: int, month: str, url: str):
    """
    Enters a new volume into the database.
    :param title: The title of the volume
    :param year: The year the volume was published
    :param month: The month the volume was published
    :param url: URL to webpage of the volume
    """
    query_database("INSERT INTO volumes (title, year, month, url) VALUES (?, ?, ?, ?)",
                   (title, year, month, url))


def insert_explored_papers_entry(pk_user: int, pk_paper: int):
    """
    Enters a new volume into the database.
    :param pk_user: Primary key of the user
    :param pk_paper: Primary key of the paper
    """
    query_database("INSERT INTO explored_papers (user, paper) VALUES (?, ?)", (pk_user, pk_paper,))


def insert_explored_authors_entry(pk_user: int, pk_author: int):
    """
    Enters a new volume into the database.
    :param pk_user: Primary key of the user
    :param pk_author: Primary key of the author
    """
    query_database("INSERT INTO explored_authors (user, author) VALUES (?, ?)", (pk_user, pk_author,))


def insert_written_by_entry(pk_paper: int, pk_author: int):
    """
    Enters a new volume into the database.
    :param pk_paper: Primary key of the paper
    :param pk_author: Primary key of the author
    """
    query_database("INSERT INTO written_by (paper, author) VALUES (?, ?)", (pk_paper, pk_author,))


def insert_coauthors_entry(pk_author1: int, pk_author2: int):
    """
    Enters a new volume into the database.
    :param pk_author1: Primary key of one author
    :param pk_author2: Primary key of the other author
    """
    query_database("INSERT INTO coauthors (author1, author2) VALUES (?, ?)", (pk_author1, pk_author2))


def insert_published_in_entry(pk_paper: int, pk_volume: int):
    """
    Enters a new volume into the database.
    :param pk_paper: Primary key of the paper
    :param pk_volume: Primary key of the volume
    """
    query_database("INSERT INTO published_in (paper, volume) VALUES (?, ?)", (pk_paper, pk_volume,))


def retrieve_user_pk_by_name(name: str):
    """
    Queries database for the primary key of the user
    :param name: Name of the user
    :return: Primary key or -1 if not in database
    """
    result = query_database("SELECT pk FROM users WHERE name = ?", (name,))
    if not result:
        return -1
    else:
        return result[0][0]


def retrieve_author_pk_by_name(name: str):
    """
    Queries database for the primary key of the author
    :param name: Name of the author
    :return: Primary key or -1 if not in database
    """
    result = query_database("SELECT pk FROM authors WHERE name = ?", (name,))
    if not result:
        return -1
    else:
        return result[0][0]


def retrieve_author_pk_by_url(url: str):
    """
    Queries database for the primary key of the author
    :param url: URL of the author
    :return: Primary key or -1 if not in database
    """
    result = query_database("SELECT pk FROM authors WHERE url = ?", (url,))
    if not result:
        return -1
    else:
        return result[0][0]


def retrieve_paper_pk_by_title(title: str):
    """
    Queries database for the primary key of the paper
    :param title: Title of the paper
    :return: Primary key or -1 if not in database
    """
    result = query_database("SELECT pk FROM papers WHERE title = ?", (title,))
    if not result:
        return -1
    else:
        return result[0][0]


def retrieve_paper_pk_by_url(url: str):
    """
    Queries database for the primary key of the paper
    :param url: URL of the paper
    :return: Primary key or -1 if not in database
    """
    result = query_database("SELECT pk FROM papers WHERE url = ?", (url,))
    if not result:
        return -1
    else:
        return result[0][0]


def retrieve_volume_pk_by_title(title: str):
    """
    Queries database for the primary key of the volume
    :param title: Title of the volume
    :return: Primary key or -1 if not in database
    """
    result = query_database("SELECT pk FROM volumes WHERE title = ?", (title,))
    if not result:
        return -1
    else:
        return result[0][0]


def retrieve_volume_pk_by_url(url: str):
    """
    Queries database for the primary key of the volume
    :param url: URL of the volume
    :return: Primary key or -1 if not in database
    """
    result = query_database("SELECT pk FROM volumes WHERE url = ?", (url,))
    if not result:
        return -1
    else:
        return result[0][0]


def retrieve_explored_papers_by_name(name: str):
    """
    Queries database for the papers the given user has explored
    :param name: Name of the user to check explored papers for
    :return:
    """

    return query_database(
        "SELECT papers.title, papers.abstract, papers.filename, papers.url FROM "
        "users "
        "INNER JOIN explored_papers ON users.pk = explored_papers.user "
        "INNER JOIN papers ON explored_papers.paper = papers.pk "
        "WHERE users.name= ?",
        (name,))


def retrieve_explored_authors_by_name(name: str):
    """
    Queries database for the authors the given user has explored
    :param name: Name of the user to check explored papers for
    :return:
    """

    return query_database(
        "SELECT authors.name, authors.url FROM "
        "users "
        "INNER JOIN explored_authors ON users.pk = explored_authors.user "
        "INNER JOIN authors ON explored_authors.author = authors.pk "
        "WHERE users.name= ?",
        (name,))


def retrieve_explored_papers_by_pk(pk: int):
    """
    Queries database for the papers the given user has explored
    :param pk: Primary key of the user to check explored papers for
    :return:
    """

    return query_database(
        "SELECT papers.title, papers.abstract, papers.filename, papers.url FROM "
        "users "
        "INNER JOIN explored_papers ON users.pk = explored_papers.user "
        "INNER JOIN papers ON explored_papers.paper = papers.pk "
        "WHERE users.pk= ?",
        (pk,))


def retrieve_explored_authors_by_pk(pk: int):
    """
    Queries database for the authors the given user has explored
    :param pk: Primary key of the user to check explored papers for
    :return:
    """

    return query_database(
        "SELECT authors.name, authors.url FROM "
        "users "
        "INNER JOIN explored_authors ON users.pk = explored_authors.user "
        "INNER JOIN authors ON explored_authors.author = authors.pk "
        "WHERE users.pk= ?",
        (pk,))


# Main execution for debugging
if __name__ == '__main__':
    clear_database()
    create_database()
    insert_papers_entry('paper1', 'abstract', 'file1.txt', 'paper link 1')
    insert_papers_entry('paper2', 'abstract', 'file2.txt', 'paper link 2')
    insert_papers_entry('paper3', 'abstract', 'file3.txt', 'paper link 3')
    insert_users_entry('Jane')
    insert_users_entry('James')
    insert_authors_entry('author1', 'link')
    insert_authors_entry('author2', 'link')
    insert_authors_entry('author3', 'link')
    insert_explored_papers_entry(1, 1)
    insert_explored_papers_entry(1, 2)
    insert_explored_papers_entry(2, 3)
    insert_explored_authors_entry(1, 1)
    insert_explored_authors_entry(1, 2)
    insert_explored_authors_entry(2, 3)

    result = retrieve_explored_authors_by_name('Jane')
    print('Jane')
    for e in result:
        print(e)

    result = retrieve_explored_authors_by_name('James')
    print('James')
    for e in result:
        print(e)

    result = retrieve_explored_authors_by_name('Hugh')
    print('Hugh')
    for e in result:
        print(e)
        clear_database()
        create_database()
