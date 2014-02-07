from datetime import datetime, timedelta
import random
import logging
import os

from models import BlogPost, Comment


def create_blog_post(title, blurb, content):

    published = datetime.now() + timedelta(days=-random.randint(1, 50))
    p = BlogPost(title=title, blurb=blurb, content=content, published=published)
    p.put()

    for i in range(0, random.randint(0, 5)):
        random_comment(p)


def random_comment(blog_post):
    possible_comments = [
        'Wow cool!',
        'Neato!',
        'Lame.',
        'First post!',
        'Was on Reddit yesterday.',
        'Pics or didn\'t happen.',
        'tl;dr was awesome',
        'I was so sad today, this made me laugh so much thanks lol.',
        'Do you think they care?',
        'Do you believe in life after love?',
        'I like this version better.',
        'That was just great.',
        'Upvoting because after reading your username, I\'m pretty sure you\'re trolling.',
        'Lol. I saw this one first and was a bit confused.',
        'I laughed so much!',
        'This is awesome',
        'Windows XP is the Playstation 2 of Operating Systems.',
        'I think we\'ve all been there at one point'
    ]

    ts = datetime.now() + timedelta(days=-random.randint(1, 50))
    c = Comment(content=possible_comments[random.randint(0, len(possible_comments)-1)], timestamp=ts, blog_post=blog_post.key)
    c.put()


def load_data_from_files(title_postfix=""):
    import_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'posts')
    for fn in os.listdir(import_dir):
        full_path = os.path.join(import_dir, fn)
        if os.path.isfile(full_path):
            with open(full_path, 'r') as f:
                title = f.readline() + title_postfix
                _ = f.readline()
                lines = f.read().split("\n\n")
                blurb = lines[0]
                content = "".join(["<p>" + p + "</p>" for p in lines])
                create_blog_post(title, blurb, content)

def create_initial_data(loads=1):
    for i in range(0, loads):
        if i == 0:
            logging.info("Loading data.")
            load_data_from_files()
        else:
            logging.info("Loading data copy %d" % (i + 1))
            load_data_from_files(" (%d)" % (i + 1))
