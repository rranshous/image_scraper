
from minimongo import Index, Model
from base import BaseModel

# TODO: embed image in blog?

class Blog(BaseModel, Model):
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
