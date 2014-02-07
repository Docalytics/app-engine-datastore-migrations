from google.appengine.ext import ndb


class BlogPost(ndb.Model):
    def __init__(self, *args, **kwargs):
        if 'slug' not in kwargs and 'title' in kwargs:
            kwargs['slug'] = BlogPost.slug_from_title(kwargs['title'])

        super(BlogPost, self).__init__(*args, **kwargs)

    @classmethod
    def slug_from_title(cls, title):
        return title.lower().replace(' ', '-').replace('\'', '').replace('"', '').replace(',', '').replace('&', '').replace('\n', '')

    title = ndb.StringProperty(required=True)
    blurb = ndb.StringProperty(required=True, indexed=False)
    content = ndb.StringProperty(required=True, indexed=False)
    published = ndb.DateTimeProperty(auto_now_add=True, required=True)
    slug = ndb.StringProperty()
    number_of_comments = ndb.IntegerProperty(default=0)


class Comment(ndb.Model):
    blog_post = ndb.KeyProperty(kind=BlogPost, required=True)
    content = ndb.StringProperty(required=True, indexed=False)
    timestamp = ndb.DateTimeProperty(required=True)
    likes = ndb.IntegerProperty(default=0)
