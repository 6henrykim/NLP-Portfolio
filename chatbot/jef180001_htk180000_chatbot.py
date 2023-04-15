"""
CS 4395.002 Human Language Technologies
Dr. Mazidi

Chatbot
Jordan Frimpter JEF 180001
Henry Kim HTK180000
Due: Apr. 15, 2023

This file is the main file to run to use the chatbot.
"""
# packages: ChatterBot2, spacy, pyyaml, requests-html
# Also run this to get package components:
# python -m spacy download en_core_web_sm

import os
import jef180001_htk180000_database as db
import jef180001_htk180000_baxter_conversation as bax_func
import jef180001_htk180000_backend as backend
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import jef180001_htk180000_baxter as baxter
import spacy

# GPU processing
spacy.prefer_gpu()

# training files
corpus_files_to_train = ["ai.yml", "botprofile.yml", "conversations.yml", "greetings.yml", "emotion.yml", "food.yml"]
corpus_new_to_train = ["ai.yml"]
topic = ["AUTHOR", "PAPER"]

# prepare path prefix
corpus_path = os.path.join(os.getcwd(), "chatterbot-corpus-master-edit")
corpus_path = os.path.join(corpus_path, "english_edit")

# other training files
corpus_path_new = os.path.join(os.getcwd(), "new-corpus")

# train bot if the training database is not present
train = not os.path.exists('db.sqlite3')

# create chatbot
chatbot = ChatBot("Barry")

# train bot if not already trained
if train:
    trainer = ChatterBotCorpusTrainer(chatbot)
    # train chatbot on the task corpus thrice [heavily reinforced responses]
    for i in range(3):
        for file in corpus_new_to_train:
            trainer.train(os.path.join(corpus_path_new, file))

    # train chatbot on english corpus
    for file in corpus_files_to_train:
        trainer.train(os.path.join(corpus_path, file))

# generate secondary database
db.create_database()


# name function
def get_user_name(in_text: str):
    """
    Prompts user for a name; adds user to database if not present.
    :param in_text: text to parse for a name
    :return: tuple of (string for name, int for user database number,
    """
    name = ""
    db_test = -1
    temp = ""

    # retrieve proper nouns
    name_candidate = bax_func.parse_proper_noun(in_text)

    # if unable to tag a name, explicitly ask for it with validation loop
    if name_candidate == "":
        print("Hmm, I can't tell if any of these words are a name. Can you tell me your name by itself?")
        name_candidate = bax_func.validation_loop()

    # confirm or deny name
    print("Is {} your name?".format(name_candidate))
    in_text = input()  # get response
    baxter_temp = baxter.seek(in_text)
    # if name rejected, enter validation loop for a better name
    if "TOKEN_YES" not in baxter_temp:
        print("Hmm. Maybe try telling me your name again?")
        name_candidate = bax_func.validation_loop()

    # accept name
    name = name_candidate
    db_test = db.retrieve_user_pk_by_name(name)
    # if name is already in database, acknowledge the return
    if db_test == -1:
        db.insert_users_entry(name)
        print("Welcome, {}. What would you like to talk about? An ACL paper, author, or something else?".format(name))
    else:
        print("Welcome back, {}.".format(name))
        temp = backend.recall_topic(db_test)

    # retrieve user key
    db_test = db.retrieve_user_pk_by_name(name)

    # return name
    return name, db_test, temp


# chatbot operation variables
in_text = ""
user_name = ""
user_dk = -1
topic = ["NONE", "PAPER", "AUTHOR"] # database can store 'none'
subtopic = ["AUTHOR_NAME", "PAPERS_AUTHORED"]
user_topic_url = ""
user_topic_code = ""
user_topic_title = ""
user_subtopic_code = ""
user_subtopic_text = ""

# initial greeting
print("Hello! I'm Barry, and I can help you with your ACL anthology research. "
      "I'm a stickler for punctuation, so I might act a little strange without it.")

# demand name
print("Can you tell me your name?")
result = get_user_name(input())

# if name given, store name and user as current user
if result[0] != "":
    user_name = result[0]
    user_dk = result[1]

    # if pre-existing user, retrieve a previous topic and set that as the current topic.
    if result[2] != "":
        user_topic_code = result[2][0]
        user_topic_url = result[2][1]
        # if paper was stored
        if user_topic_code == "PAPER":
            user_topic_title = backend.explore_paper_title(user_dk, user_topic_url)
            print("Since we last spoke, I've been thinking about the paper '{}' "
                  "that I previously mentioned to you.".format(user_topic_title))
        # if author was stored
        if user_topic_code == "AUTHOR":
            user_topic_title = backend.explore_author_name(user_dk, user_topic_url)
            print("Since we last spoke, I've been thinking about the author {} "
                  "that I previously mentioned to you.".format(user_topic_title))
        # if no code was stored
        if user_topic_code == "NONE":
            user_topic_url = ""
            user_topic_code = ""
            user_topic_title = ""
            print("What would you like to talk about? An ACL paper, author, or something else?")

while True:
    # get user text
    in_text = input()

    # scan text for tokens; simplified response if no name [lock features]
    if user_name:
        baxter_tokens = baxter.seek(in_text)
    else:
        baxter_tokens = baxter.seek_simple(in_text)

    # behavior switches

    # function code to exit
    if "FUNC_EXIT" in baxter_tokens:
        # ask for confirmation
        print("Is it time for you to leave?")
        baxter_temp = baxter.seek(input())

        # if yes, exit. Else, continue
        if "TOKEN_YES" in baxter_temp:
            # change functionality if a name was stored
            if user_name:
                print("Goodbye, {}.".format(user_name))
            else:
                print("Goodbye.")
            break

        # if not yes, remain
        print("Ah, I was mistaken.")
        continue

    # print help
    if "FUNC_HELP" in baxter_tokens:
        print("I can help with looking up information on papers and authors in the ACL database.")
        print("To get started, try asking to talk about a paper or an author.")
        continue

    # demand name
    if "FUNC_DEMAND_NAME" in baxter_tokens:
        print("Please tell me your name before making any further requests.")
        continue

    # get name
    if "FUNC_NAME" in baxter_tokens:
        result = get_user_name(in_text)
        # if name retrieved
        if result[0] != "":
            # store name
            user_name = result[0]
            user_dk = result[1]
            # if returning user, case switch between previous topics
            if result[2] != "":
                user_topic_code = result[2][0]
                user_topic_url = result[2][1]
                if user_topic_code == "PAPER":
                    user_topic_title = backend.explore_paper_title(user_dk, user_topic_url)
                    print("Since we last spoke, I've been thinking about the paper '{}' "
                          "that I previously mentioned to you.".format(user_topic_title))
                if user_topic_code == "AUTHOR":
                    user_topic_title = backend.explore_author_name(user_dk, user_topic_url)
                    print("Since we last spoke, I've been thinking about the author {} "
                          "that I previously mentioned to you.".format(user_topic_title))
                if user_topic_code == "NONE":
                    user_topic_url = ""
                    user_topic_code = ""
                    user_topic_title = ""
                    print("What would you like to talk about? An ACL paper, author, or something else?")
            else:
                user_topic_url = ""
                user_topic_code = ""
                user_topic_title = ""

            user_subtopic_code = ""
            user_subtopic_text = ""

    # if current task is papers
    if user_topic_code == "PAPER":
        # provide paper abstract
        if "TOKEN_ABSTRACT" in baxter_tokens:
            temp = backend.explore_paper_abstract(user_dk, user_topic_url)
            if not temp or temp == '':
                print("Hmm... I can't find the abstract for '{}'."
                      "I can tell you about its authors or publish date, though".format(user_topic_title))
            else:
                print("Here's the abstract for '{}':\" {}\"".format(user_topic_title, bax_func.line_segment(temp, 15)))
            continue
        # provide filepath of paper
        if "TOKEN_FILEPATH" in baxter_tokens:
            temp = backend.explore_paper_filepath(user_dk, user_topic_url)
            print("Here's the filepath for '{}':\n{}".format(user_topic_title, temp))
            continue
        # provide writing date
        if "TOKEN_DATE" in baxter_tokens:
            temp = backend.explore_paper_date(user_dk, user_topic_url)
            print("The paper '{}' was published on {}".format(user_topic_title, temp))
            continue

    if user_topic_code == "AUTHOR":
        # provide coauthors
        if "TOKEN_COAUTHOR" in baxter_tokens:
            temp = backend.explore_author_coauthors(user_dk, user_topic_url)
            out = bax_func.list_display(temp)
            print("Here are {}'s coauthors:\n{}".format(user_topic_title, out))
            continue

    # display topic if topic exists and is mentioned
    if "TOKEN_TOPIC" in baxter_tokens:
        if user_topic_code == "":
            print("We haven't picked a topic to discuss yet.")
        if user_topic_code == "PAPER":
            print("We are currently discussing the paper '{}'.".format(user_topic_title))
        if user_topic_code == "AUTHOR":
            print("We are currently discussing the author '{}'".format(user_topic_title))

    # if author or paper is mentioned without a topic, fall into topic search
    if "FUNC_PAPER_OR_AUTHOR" in baxter_tokens:

        # if no topic, shift to topic search
        if user_topic_code == "":
            baxter_tokens.append("FUNC_TOPIC")

        # if topic is paper, retrieve authors as subtopic
        elif user_topic_code == "PAPER":
            user_subtopic_code = "AUTHOR_NAME"
            print("Let me go looking...")
            user_subtopic_text = backend.explore_paper_authors(user_dk, user_topic_url)
            out = bax_func.list_display(user_subtopic_text)
            print("Here are the authors of the paper '{}':\n{}".format(user_topic_title, out))

        # if topic is author, retrieve papers as subtopic
        elif user_topic_code == "AUTHOR":
            user_subtopic_code = "PAPERS_AUTHORED"
            print("Let me go looking...")
            user_subtopic_text = backend.explore_author_papers(user_dk, user_topic_url)
            out = bax_func.list_display(user_subtopic_text)
            print("Here are some papers written by {}:\n{}".format(user_topic_title, out))

    # change topic function
    if "FUNC_TOPIC" in baxter_tokens:
        # pretest for switch topic to paper from author
        if user_subtopic_code == "AUTHOR_NAME":
            temp = bax_func.pair_tokens(in_text, user_subtopic_text)
            # if there was an author match
            if temp != "":
                user_topic_code = "AUTHOR"
                user_topic_url = backend.explore_author(user_dk, temp[0])
                user_topic_title = backend.explore_author_name(user_dk, user_topic_url)
                user_subtopic_text = ""
                user_subtopic_code = ""
                print("Alright, let's talk about {}.".format(user_topic_title))
                continue

        # request a new topic
        print("Just to clarify, would you like to talk about authors or papers?")
        in_temp = input()
        baxter_temp = baxter.seek(in_temp)

        # if author, switch topic to an author
        if "TOKEN_AUTHOR" in baxter_temp:
            print("Ok, let's talk about an author. What is the name of the author you want to talk about?")
            user_topic_code = "AUTHOR"
            temp = bax_func.validation_loop()
            print("Let me go look for that...")
            user_topic_url = backend.explore_author(user_dk, temp)
            user_topic_title = backend.explore_author_name(user_dk, user_topic_url)
            print("I found an author named {}. I can tell you about "
                  "their papers and co-authors.".format(user_topic_title))

            # clear subtopic
            user_subtopic_text = ""
            user_subtopic_code = ""

        # if paper, switch topic to a paper
        elif "TOKEN_PAPER" in baxter_temp:
            print("Ok, let's talk about a paper. What is the subject or title of the paper you want to talk about?")
            user_topic_code = "PAPER"
            temp = bax_func.validation_loop()
            print("Let me go look for that...")
            user_topic_url = backend.explore_paper(user_dk, temp)
            user_topic_title = backend.explore_paper_title(user_dk, user_topic_url)
            print("I found a paper called '{}'. I can tell you about "
                  "its authors, abstract, and publish date.".format(user_topic_title))

            # clear subtopic
            user_subtopic_text = ""
            user_subtopic_code = ""

        else:
            print("I don't recognize that topic, sorry. I only talk about authors and papers.")

    # no function detected
    if "FUNC_NONE" in baxter_tokens:
        # permit Barry to respond
        print(chatbot.get_response(in_text))
        continue
