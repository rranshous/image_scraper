
from minimongo import Index, Model
from base import BaseModel

class Blog(BaseModel, Model):
    class Meta:
        database = "scrape_images"
        collection = "blogs"

        indices = (
            Index("url"),
            Index("short_hash"),
            Index("categories") # list of categories
        )

