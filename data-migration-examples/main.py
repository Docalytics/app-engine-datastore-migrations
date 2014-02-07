import os
import webapp2
import jinja2
import logging

from google.appengine.ext import deferred

from models import BlogPost, Comment
import bootstrap
import basic_migration
import mapreduce_migration

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class BaseHandler(webapp2.RequestHandler):
    def render_response(self, _template, **kwargs):
        template = JINJA_ENVIRONMENT.get_template(_template)
        self.response.write(template.render(**kwargs))


class MainHandler(BaseHandler):
    def get(self):
        self.render_response("default.html")


class ViewPostsHandler(BaseHandler):
    def get(self):
        some_posts = BlogPost.query().order(-BlogPost.published).fetch(limit=5)
        self.render_response("display_blog.html", posts=some_posts)


class DisplayPostHandler(BaseHandler):
    def get(self, slug):
        post = BlogPost.query(BlogPost.slug == slug).get()
        comments = Comment.query(Comment.blog_post == post.key).fetch(limit=10)
        self.render_response("display_post.html", post=post, comments=comments)


class CreateSlugsHandler(BaseHandler):
    def get(self):
        deferred.defer(basic_migration.add_slugs)
        self.redirect("/")


class CreateSlugsMapReduceHandler(BaseHandler):
    def get(self):
        pipeline = mapreduce_migration.CreateSlugsPipeline()
        pipeline.start()
        self.redirect("/")


class DeleteSlugsHandler(BaseHandler):
    def get(self):
        deferred.defer(basic_migration.delete_slugs)
        self.redirect("/")


class CountCommentsHandler(BaseHandler):
    def get(self):
        deferred.defer(basic_migration.count_comments)
        self.redirect("/")


class CountCommentsMapReduceHandler(BaseHandler):
    def get(self):
        pipeline = mapreduce_migration.CountCommentsPipeline()
        pipeline.start()
        self.redirect("/")

class DeleteCommentCountsHandler(BaseHandler):
    def get(self):
        deferred.defer(basic_migration.delete_comment_counts)
        self.redirect("/")


class BootstrapHandler(BaseHandler):
    def get(self):
        bootstrap.create_initial_data(100)
        self.redirect("/")


from google.appengine.ext import db

class Lion(db.Model):
    @classmethod
    def kind(cls):
        return "Cat"

    name = db.StringProperty()
    height = db.IntegerProperty()
    mass = db.IntegerProperty(name="weight")

class TestHandler(BaseHandler):
    def get(self):
        #Cat(name="fido", height=20, weight=500).put()
        #Cat(name="garfield", height=15, weight=700).put()
        #Cat(name="lionel", height=22, weight=250).put()
        #Cat(name="Misty", height=21, weight=199).put()
        #Lion(name="Jerry", height=23, weight=300).put()
        logging.warning("Cats over 500g: %d" % db.GqlQuery("SELECT * FROM Cat WHERE weight > 500").count(limit=10))

        self.redirect("/")


app = webapp2.WSGIApplication([
    webapp2.Route(r'/', "main.MainHandler"),
    webapp2.Route(r'/bootstrap', "main.BootstrapHandler"),
    webapp2.Route(r'/view-posts', "main.ViewPostsHandler"),
    webapp2.Route(r'/create-slugs', "main.CreateSlugsHandler"),
    webapp2.Route(r'/create-slugs-mapreduce', "main.CreateSlugsMapReduceHandler"),
    webapp2.Route(r'/delete-slugs', "main.DeleteSlugsHandler"),
    webapp2.Route(r'/count-comments', "main.CountCommentsHandler"),
    webapp2.Route(r'/count-comments-mapreduce', "main.CountCommentsMapReduceHandler"),
    webapp2.Route(r'/delete-comment-counts', "main.DeleteCommentCountsHandler"),
    webapp2.Route(r'/posts/<slug>', "main.DisplayPostHandler"),
    webapp2.Route(r'/test', "main.TestHandler"),
], debug=True)
