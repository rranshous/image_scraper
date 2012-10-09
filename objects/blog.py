
from minimongo import Model, Index

# TODO: embed image in blog?

class Blog(Model):
    class Meta:
        database = "scrape_images"
        collection = "blogs"

        indices = (
            Index("url"),
            # TODO: figure out how to index urls in hash keys
            # Index("blog_urls"),
            # Index("is_stored"),
            Index("short_hash")
        )

    def __getattr__(self, attr):
        """
        over write getattr to return None when
        we try and get the value of a non-existant
        attr rather than throwing an exception
        """

        try:
            return super(Blog, self).__getattr__(attr)
        except AttributeError:
            return None
