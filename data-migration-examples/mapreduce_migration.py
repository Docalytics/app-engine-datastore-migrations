import logging
from google.appengine.ext import ndb
from mapreduce import base_handler, mapper_pipeline, operation, mapreduce_pipeline
from models import BlogPost

def count_comments_mapper(comment):
    yield (comment.blog_post.urlsafe(), "")


def count_comments_reducer(keystring, values):
    post = ndb.Key(urlsafe=keystring).get()
    post.number_of_comments = len(values)
    logging.info("%s ==> %d" % (post.slug, post.number_of_comments))
    yield operation.db.Put(post)


class CountCommentsPipeline(base_handler.PipelineBase):
    def run(self):
        yield mapreduce_pipeline.MapreducePipeline(
            job_name="count comments",
            mapper_spec="mapreduce_migration.count_comments_mapper",
            reducer_spec="mapreduce_migration.count_comments_reducer",
            input_reader_spec="mapreduce.input_readers.DatastoreInputReader",
            mapper_params={
                "entity_kind": "models.Comment"
            },
            shards=16)


def create_slug_mapper(post):
    post.slug = BlogPost.slug_from_title(post.title)
    yield operation.db.Put(post)


class CreateSlugsPipeline(base_handler.PipelineBase):
    def run(self):
        yield mapper_pipeline.MapperPipeline(
            job_name="create slug",
            handler_spec="mapreduce_migration.create_slug_mapper",
            input_reader_spec="mapreduce.input_readers.DatastoreInputReader",
            params={
                "entity_kind": "models.BlogPost"
            },
            shards=16)