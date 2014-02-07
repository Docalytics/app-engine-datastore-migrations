import logging
from models import BlogPost, Comment
from google.appengine.ext import deferred
from google.appengine.ext import ndb

# Ideal batch size may vary based on entity size.
BATCH_SIZE = 10


def add_slugs(cursor=None, num_updated=0):
    posts, next_cursor, is_there_more = BlogPost.query().fetch_page(BATCH_SIZE, start_cursor=cursor)

    for p in posts:
        # Create a slug from the title
        p.slug = BlogPost.slug_from_title(p.title)

    if len(posts) > 0:
        ndb.put_multi(posts)
        num_updated += len(posts)
        logging.info('Updated %d entities to Datastore for a total of %d', len(posts), num_updated)
    else:
        logging.info('Schema update complete with %d updates!', num_updated)

    if is_there_more:
        deferred.defer(add_slugs, cursor=next_cursor, num_updated=num_updated)


def delete_slugs(cursor=None, num_updated=0):
    posts, next_cursor, is_there_more = BlogPost.query().fetch_page(BATCH_SIZE, start_cursor=cursor)

    for p in posts:
        if 'slug' in p._properties:
            del p._properties['slug']

    if len(posts) > 0:
        ndb.put_multi(posts)
        num_updated += len(posts)
        logging.info('Updated %d entities to Datastore for a total of %d', len(posts), num_updated)
    else:
        logging.info('Schema update complete with %d updates!', num_updated)

    if is_there_more:
        deferred.defer(delete_slugs, cursor=next_cursor, num_updated=num_updated)


@ndb.toplevel
def count_comments(cursor=None, num_updated=0):
    posts, next_cursor, is_there_more = BlogPost.query().fetch_page(BATCH_SIZE, start_cursor=cursor)

    for p in posts:
        # Count the comments
        p.number_of_comments = Comment.query(Comment.blog_post == p.key).count(limit=1000)
        p.put_async()

    if len(posts) > 0:
        num_updated += len(posts)
        logging.info('Updated %d entities to Datastore for a total of %d', len(posts), num_updated)
    else:
        logging.info('Schema update complete with %d updates!', num_updated)

    if is_there_more:
        deferred.defer(count_comments, cursor=next_cursor, num_updated=num_updated)


def delete_comment_counts(cursor=None, num_updated=0):
    posts, next_cursor, is_there_more = BlogPost.query().fetch_page(BATCH_SIZE, start_cursor=cursor)

    for p in posts:
        if 'number_of_comments' in p._properties:
            del p._properties['number_of_comments']

    if len(posts) > 0:
        ndb.put_multi(posts)
        num_updated += len(posts)
        logging.info('Updated %d entities to Datastore for a total of %d', len(posts), num_updated)
    else:
        logging.info('Schema update complete with %d updates!', num_updated)

    if is_there_more:
        deferred.defer(delete_comment_counts, cursor=next_cursor, num_updated=num_updated)