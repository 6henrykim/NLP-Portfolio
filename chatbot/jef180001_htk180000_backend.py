"""
CS 4395.002 Human Language Technologies
Dr. Mazidi

Chatbot
Jordan Frimpter JEF 180001
Henry Kim HTK180000
Due: Apr. 15, 2023

This file provides functions for combining the webscraping and database backends with the chatbot interface.
"""

import jef180001_htk180000_database as db
import jef180001_htk180000_webscraping as ws
import os
import random


def redirect_volume_to_paper(volume_url: str):
    """
    Queries the database for a paper published in the volume to show the user instead of the volume.
    :param volume_url: URL of the volume
    :return: A URL of a paper in the volume
    """
    paper_links = db.query_database("SELECT papers.url FROM "
                                    "papers INNER JOIN published_in ON papers.pk=published_in.paper "
                                    "INNER JOIN volumes ON published_in.volume=volumes.pk "
                                    "WHERE volumes.url = ?", (volume_url,))

    # TODO: potential improvement: can randomize which link gets returned
    return paper_links[-1][0]


def explore_topic(user_pk: int, topic: str):
    """
    Searches the ACL anthology for a topic, adds the first result to the database and returns a url link to be used
    as the active topic.
    :param user_pk: Primary key of the user
    :param topic: Topic to search for
    :return: URL for the topic scraped
    """
    link = ws.search_and_scrape(topic)

    if 'people' in link:  # Author page
        author_pk = db.retrieve_author_pk_by_url(link)
        db.insert_explored_authors_entry(user_pk, author_pk)
    elif 'volumes' in link:  # Publishing volume page
        # Redirect to a paper instead, once a volume is scraped, some of its papers should have been scraped too
        link = redirect_volume_to_paper(link)
        paper_pk = db.retrieve_paper_pk_by_url(link)
        db.insert_explored_papers_entry(user_pk, paper_pk)
    else:  # Otherwise assume it is a paper page
        paper_pk = db.retrieve_paper_pk_by_url(link)
        db.insert_explored_papers_entry(user_pk, paper_pk)

    return link


def explore_author(user_pk: int, name: str):
    """
    Searches the ACL anthology for an author and scrapes it.
    We use the ACL search function to compensate for any misspelling of the author's name.
    If a paper or volume is found, it will still scrape it.
    :param user_pk: Primary key of the user
    :param name: Name of the author to search for
    :return: URL for the author scraped
    """
    # ACL Anthology search uses Google backend, so we can use keywords to modify the search to focus on people pages
    link = ws.search_and_scrape("people " + name)

    if 'people' in link:  # Author page
        author_pk = db.retrieve_author_pk_by_url(link)
        db.insert_explored_authors_entry(user_pk, author_pk)
    elif 'volumes' in link:  # Publishing volume page
        # Redirect to a paper instead, once a volume is scraped, some of its papers should have been scraped too
        link = redirect_volume_to_paper(link)
        paper_pk = db.retrieve_paper_pk_by_url(link)
        db.insert_explored_papers_entry(user_pk, paper_pk)
    else:  # Otherwise assume it is a paper page
        paper_pk = db.retrieve_paper_pk_by_url(link)
        db.insert_explored_papers_entry(user_pk, paper_pk)

    return link


def explore_paper(user_pk: int, title: str):
    """
    Searches the ACL anthology for a paper page and scrapes it.
    Best used for keywords or exact title.
    If it finds a volume or author page instead, it will still scrape it.
    :param user_pk: Primary key of the user
    :param title: Title to search for
    :return: URL for the paper scraped
    """

    # ACL Anthology search uses Google backend, so we can use keywords to modify the search to ignore people and volumes
    link = ws.search_and_scrape("-people -volumes " + title)

    if 'people' in link:  # Author page
        author_pk = db.retrieve_author_pk_by_url(link)
        db.insert_explored_authors_entry(user_pk, author_pk)
    elif 'volumes' in link:  # Publishing volume page
        # Redirect to a paper instead, once a volume is scraped, some of its papers should have been scraped too
        link = redirect_volume_to_paper(link)
        paper_pk = db.retrieve_paper_pk_by_url(link)
        db.insert_explored_papers_entry(user_pk, paper_pk)
    else:  # Otherwise assume it is a paper page
        paper_pk = db.retrieve_paper_pk_by_url(link)
        db.insert_explored_papers_entry(user_pk, paper_pk)

    return link


def explore_paper_authors(user_pk: int, paper_url: str):
    """
    Queries the database for the authors of a paper.
    Resulting authors are noted as explored by the user.
    :param user_pk: Primary key of the user
    :param paper_url: URL of the paper
    :return: A list of tuples (author name, author url)
    """
    authors = db.query_database("SELECT authors.pk, authors.name, authors.url FROM authors "
                                "INNER JOIN written_by ON authors.pk=written_by.author "
                                "INNER JOIN papers ON written_by.paper=papers.pk "
                                "WHERE papers.url = ?", (paper_url,))

    # If empty query result, explore the paper and try again
    if not authors:
        paper_url = explore_paper(user_pk, paper_url)
        authors = db.query_database("SELECT authors.pk, authors.name, authors.url FROM authors "
                                    "INNER JOIN written_by ON authors.pk=written_by.author "
                                    "INNER JOIN papers ON written_by.paper=papers.pk "
                                    "WHERE papers.url = ?", (paper_url,))

    for author in authors:
        db.insert_explored_authors_entry(user_pk, author[0])

    # Remove primary key from query result
    return [(author[1], author[2]) for author in authors]


def explore_paper_abstract(user_pk: int, paper_url: str):
    """
    Queries the database for the abstract of a paper.
    :param user_pk: Primary key of the user
    :param paper_url: URL of the paper
    :return: The text of the abstract
    """

    abstract = db.query_database("SELECT papers.abstract FROM papers "
                                 "WHERE papers.url = ?", (paper_url,))

    # If empty query result, explore the paper and try again
    if not abstract:
        paper_url = explore_paper(user_pk, paper_url)
        abstract = db.query_database("SELECT papers.abstract FROM papers "
                                     "WHERE papers.url = ?", (paper_url,))

    return abstract[0][0]


def explore_paper_title(user_pk: int, paper_url: str):
    """
    Queries the database for the title of a paper.
    :param user_pk: Primary key of the user
    :param paper_url: URL of the paper
    :return: The text of the title
    """

    title = db.query_database("SELECT papers.title FROM papers "
                              "WHERE papers.url = ?", (paper_url,))

    # If empty query result, explore the paper and try again
    if not title:
        paper_url = explore_paper(user_pk, paper_url)
        title = db.query_database("SELECT papers.title FROM papers "
                                  "WHERE papers.url = ?", (paper_url,))

    return title[0][0]


def explore_paper_filepath(user_pk: int, paper_url: str):
    """
    Queries the database for the filepath of a paper.
    :param user_pk: Primary key of the user
    :param paper_url: URL of the paper
    :return: The text of the filepath
    """

    filename = db.query_database("SELECT papers.filename FROM papers "
                                 "WHERE papers.url = ?", (paper_url,))

    # If empty query result, explore the paper and try again
    if not filename:
        paper_url = explore_paper(user_pk, paper_url)
        filename = db.query_database("SELECT papers.filename FROM papers "
                                     "WHERE papers.url = ?", (paper_url,))

    return os.path.join(ws.save_filepath, filename[0][0])


def explore_paper_date(user_pk: int, paper_url: str):
    """
    Queries the database for the publishling date of a paper.
    :param user_pk: Primary key of the user
    :param paper_url: URL of the paper
    :return: A string with the month and date
    """

    date = db.query_database("SELECT volumes.month, volumes.year FROM volumes "
                             "INNER JOIN published_in ON published_in.volume=volumes.pk "
                             "INNER JOIN papers ON published_in.paper=papers.pk "
                             "WHERE papers.url = ?", (paper_url,))

    # If empty query result, explore the paper and try again
    if not date:
        paper_url = explore_paper(user_pk, paper_url)
        date = db.query_database("SELECT volumes.month, volumes.year FROM volumes "
                                 "INNER JOIN published_in ON published_in.volume=volumes.pk "
                                 "INNER JOIN papers ON published_in.paper=papers.pk "
                                 "WHERE papers.url = ?", (paper_url,))

    return date[0][0] + ", " + str(date[0][1])


def explore_author_name(user_pk: int, author_url: str):
    """
    Queries the database for the name of an author.
    :param user_pk: Primary key of the user
    :param author_url: URL of the author
    :return: The text of the title
    """

    name = db.query_database("SELECT authors.name FROM authors "
                             "WHERE authors.url = ?", (author_url,))

    # If empty query result, explore the paper and try again
    if not name:
        author_url = explore_author(user_pk, author_url)
        name = db.query_database("SELECT authors.name FROM authors "
                                 "WHERE authors.url = ?", (author_url,))

    return name[0][0]


def explore_author_papers(user_pk: int, author_url: str):
    """
    Queries the database for the papers written by the author.
    Resulting papers are noted as explored by the user.
    :param user_pk: Primary key of the user
    :param author_url: URL of the paper
    :return: A list of tuples (paper title, paper url)
    """
    papers = db.query_database("SELECT papers.pk, papers.title, papers.url FROM papers "
                               "INNER JOIN written_by ON papers.pk=written_by.paper "
                               "INNER JOIN authors ON written_by.author=authors.pk "
                               "WHERE authors.url = ?", (author_url,))

    # If empty query result, explore the author and try again
    if not papers:
        author_url = explore_author(user_pk, author_url)
        papers = db.query_database("SELECT papers.pk, papers.title, papers.url FROM papers "
                                   "INNER JOIN written_by ON papers.pk=written_by.paper "
                                   "INNER JOIN authors ON written_by.author=authors.pk "
                                   "WHERE authors.url = ?", (author_url,))

    for paper in papers:
        db.insert_explored_papers_entry(user_pk, paper[0])

    # Remove primary key from query result
    return [(paper[1], paper[2]) for paper in papers]


def explore_author_coauthors(user_pk: int, author_url: str):
    """
    Queries the database for the coauthors written of the author. Resulting authors are noted as explored by the user.
    :param user_pk: Primary key of the user
    :param author_url: URL of the paper
    :return: A list of tuples (author name, author url)
    """
    authors = db.query_database("SELECT r.pk, r.name, r.url FROM authors l "
                                "INNER JOIN coauthors ON l.pk=coauthors.author1 "
                                "INNER JOIN authors r ON coauthors.author2=r.pk "
                                "WHERE l.url = ?", (author_url,))

    # If empty query result, explore the author and try again
    if not authors:
        author_url = explore_author(user_pk, author_url)
        authors = db.query_database("SELECT r.pk, r.name, r.url FROM authors l "
                                    "INNER JOIN coauthors ON l.pk=coauthors.author1 "
                                    "INNER JOIN authors r ON coauthors.author2=r.pk "
                                    "WHERE l.url = ?", (author_url,))

    for author in authors:
        db.insert_explored_authors_entry(user_pk, author[0])

    # Remove primary key from query result
    return [(author[1], author[2]) for author in authors]


def recall_paper(pk_user: int):
    """
    Recalls a random paper that has been explored previously.
    :param pk_user: Primary key of user
    :return: A tuple of a paper (paper title, paper url)
    """
    papers = db.retrieve_explored_papers_by_pk(pk_user)

    if not papers:
        return None

    r = random.randint(0, len(papers) - 1)
    return papers[r][0], papers[r][3]


def recall_author(pk_user: int):
    """
    Recalls a random author that has been explored previously.
    :param pk_user: Primary key of user
    :return: A tuple of an author (author name, author url)
    """
    authors = db.retrieve_explored_authors_by_pk(pk_user)

    if not authors:
        return None

    r = random.randint(0, len(authors) - 1)
    return authors[r][0], authors[r][1]


def recall_topic(pk_user: int):
    """
    Recalls a topic that the user has explored previously.
    :param pk_user: Primary key of user
    :return: A tuple of the topic (topic type, url). The topic type can be NONE, AUTHOR, or PAPER.
    """

    # Prioritize finding a paper, if no paper found, try to find an author
    topic = recall_paper(pk_user)

    # Try to recall an author
    if not topic:
        topic = recall_author(pk_user)

    # Return nothing
    if not topic:
        return 'NONE', None

    topic_url = topic[1]

    if 'people' in topic_url:
        return 'AUTHOR', topic_url
    else:
        return 'PAPER', topic_url


# Main execution for debugging
if __name__ == '__main__':
    db.clear_database()
    db.create_database()
    db.insert_users_entry('Test')
    print(recall_topic(1))
    print(explore_author(1, 'sergui'))
    print(recall_topic(1))
