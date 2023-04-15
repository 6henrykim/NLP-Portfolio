"""
CS 4395.002 Human Language Technologies
Dr. Mazidi

Chatbot
Jordan Frimpter JEF 180001
Henry Kim HTK180000
Due: Apr. 15, 2023

This file provides functions for the webscraping backend of the chatbot. It scrapes data on articles and authors
from the ACL Anthology.

Reference Code
https://www.geeksforgeeks.org/downloading-pdfs-with-python-using-requests-and-beautifulsoup/
https://pypdf.readthedocs.io/en/stable/user/extract-text.html
"""

import jef180001_htk180000_database as db
from bs4 import BeautifulSoup
import re
import requests
from requests_html import HTMLSession
import os

base_url = 'https://aclanthology.org'
save_filepath = 'papers'


def scrape_author_page(url: str):
    """
    Scrapes the author page from the URL and adds them to the database.
    Anyone listed as a coauthor is added to the database as well and a coauthor relation is added.
    It also scrapes the page of the 5 most recent papers, see the scrape_paper_page function.
    :param url: URL of page to scrape
    :return: Primary key of the author scraped
    """
    # Request the page and store it as a soup object
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, features='html.parser')

    # Collect author name and put in database
    author_name = soup.find('h2').text
    db.insert_authors_entry(author_name, url)
    author_pk = db.retrieve_author_pk_by_url(url)

    # Collect a elements. Links for authors and papers have the class align-middle
    a_elements = [e for e in soup.find_all('a') if e.get('class') and 'align-middle' in e.get('class')]

    # Coauthor pages all have 'people' in their links
    coauthor_elements = [e for e in a_elements if 'people' in e.get('href')]

    # Add to the coauthors to database
    for e in coauthor_elements:
        # Insert the coauthur into authors table
        author_name = e.text
        author_url = base_url + e.get('href')
        db.insert_authors_entry(author_name, author_url)

        # Add relation between the authors in the coauthor table
        author2_pk = db.retrieve_author_pk_by_url(author_url)
        db.insert_coauthors_entry(author_pk, author2_pk)

    # Can only get the pdf links but the main page for the paper is the same link with .pdf dropped off
    paper_links = [e.get('href')[:-4] + '/' for e in a_elements if '.pdf' in e.get('href')]

    # TODO: Possible improvement: give option to choose these papers at random
    # Scrape papers from the list
    limit = len(paper_links) if len(paper_links) < 5 else 5
    for link in paper_links[:5]:
        scrape_paper_page(link)

    # Return primary key of scraped paper
    return author_pk


def scrape_paper_page(url: str):
    """
    Scrapes the information from a paper page to get the title, authors, publication volume, and abstract.
    It also downloads a pdf copy of the pdf associated with the page. Anyone listed as an author is added to the
    database, but they aren't listed as coauthors of each other until their author page is visited.
    :param url: URL of the page to scrape
    :return: Primary key of the scraped paper
    """

    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, features='html.parser')

    # Title of the paper is the first h2 heading
    title = soup.find('h2').text
    # Use the title without punctuation and removed spaces as the filename
    filename = re.sub(r'[^\w\s]', '', title).replace(' ', '_').lower() + ".pdf"

    # Get the abstract if one is present
    abstract = ''
    span_elements = soup.find_all('span')
    for e in span_elements:
        # The abstract is nested under an element with the 'acl-abstract' class
        if e.parent.get('class') and 'acl-abstract' in e.parent.get('class'):
            abstract = e.text

    # Insert paper into database
    url = url + '/' if not url.endswith('/') else url
    db.insert_papers_entry(title, abstract, filename, url)
    paper_pk = db.retrieve_paper_pk_by_url(url)

    # Get the authors and add written by relation
    author_elements = [e for e in soup.find_all('a') if 'people' in e.get('href')]
    for e in author_elements:
        author_name = e.text
        author_url = base_url + e.get('href')
        db.insert_authors_entry(author_name, author_url)
        author_pk = db.retrieve_author_pk_by_url(author_url)
        db.insert_written_by_entry(paper_pk, author_pk)

    # Get the publication volume data
    volume_title_element = [e for e in soup.find_all('a') if 'volumes' in e.get('href')][0]
    volume_url = base_url + volume_title_element.get('href')
    # Month and year are dd elements with sibling elements that label them
    table_elements = soup.find_all('dd')
    volume_month = [e for e in table_elements if 'Month' in e.previous_sibling.text][0].text
    volume_year = [e for e in table_elements if 'Year' in e.previous_sibling.text][0].text

    # Insert the publication volume information into the table
    db.insert_volumes_entry(volume_title_element.text, int(volume_year), volume_month, volume_url)
    volume_pk = db.retrieve_volume_pk_by_url(volume_url)
    # Add relation between the paper and the volume it was published in
    db.insert_published_in_entry(paper_pk, volume_pk)

    # Download the pdf and save it
    pdf_url = url[:-1] if url.endswith('/') else url
    pdf_url += '.pdf'
    r = requests.get(pdf_url)

    # If a folder for the papers doesn't exist, make one
    if not os.path.exists(save_filepath):
        os.makedirs(save_filepath)

    filepath = os.path.join(save_filepath, filename)
    pdf = open(filepath, 'wb')
    pdf.write(r.content)
    pdf.close()

    # Return primary key of scraped paper
    return paper_pk


def scrape_volume_page(url: str):
    """
    Scrapes the information from a publishing volume page to get the title, month, and year.
    It also downloads the first 5 papers listed.
    :param url: URL of the page to scrape
    :return: Primary key of the scraped volume
    """

    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, features='html.parser')

    # Collect a elements. Links for papers have the class align-middle
    a_elements = [e for e in soup.find_all('a') if e.get('class') and 'align-middle' in e.get('class')]

    # Can only get the pdf links but the main page for the paper is the same link with .pdf dropped off
    paper_links = [e.get('href')[:-4] + '/' for e in a_elements if
                   '.pdf' in e.get('href') and 'attachments' not in e.get('href')]

    volume_title = soup.find('h2').text

    # Month and year are dd elements with sibling elements that label them
    table_elements = soup.find_all('dd')
    volume_month = [e for e in table_elements if 'Month' in e.previous_sibling.text][0].text
    volume_year = [e for e in table_elements if 'Year' in e.previous_sibling.text][0].text

    # Insert volume entry
    db.insert_volumes_entry(volume_title, str(volume_year), volume_month, url)
    volume_pk = db.retrieve_volume_pk_by_url(url)

    # TODO: Give option to choose these papers at random
    # Scrape papers from the list
    for link in paper_links[:5]:
        scrape_paper_page(link)

    return volume_pk


def search_topics(topic: str):
    """
    Scrapes the ACL Anthology search page to get a list of links and returns the top result.
    :param topic: A string to use as the search query
    :return: A tuple of URL of the result and the text representing it
    """

    url = "https://aclanthology.org/search/?q=" + topic.replace(' ', '+')

    # For the search function to work we need JavaScript, so we'll use the requests-html library
    session = HTMLSession()
    r = session.get(url)
    # This executes the JavaScript
    r.html.render()

    # Find the links
    a_elements = r.html.find('a')
    # Choose only links that came from the search function, these have the gs-title as a value in the class attribute
    a_elements = [e for e in a_elements if ('gs-title',) in e.attrs.values() and 'html(title)' not in e.attrs.values()]

    # Remove elements that have duplicate text
    unique_elements = []
    unique_text = []
    for e in a_elements:
        if e.text not in unique_text:
            unique_text.append(e.text)
            unique_elements.append(e)

    # TODO: Could make this non-deterministic and choose one of the top choices at random
    res = unique_elements[0]

    return res.attrs['href'], res.text


def search_and_scrape(topic: str):
    """
    Calls the search_topics function, determines the type of link returned and then scrapes that page.
    :param topic: A string to use as the search query
    :return: The link that was scraped, can be used to get primary key of an author, volume, or paper
    """
    link, link_description = search_topics(topic)
    link = link + '/' if not link.endswith('/') else link

    if 'people' in link:  # Author page
        scrape_author_page(link)
    elif 'volumes' in link:  # Publishing volume page
        scrape_volume_page(link)
    else:  # Otherwise assume it is a paper page
        scrape_paper_page(link)

    return link


# Main execution for debugging
if __name__ == '__main__':
    db.clear_database()
    db.create_database()
    print(search_and_scrape('dog'))
    db.insert_users_entry('Darla')
    db.insert_explored_papers_entry(1, 1)
    print(db.retrieve_explored_papers_by_pk(1))
