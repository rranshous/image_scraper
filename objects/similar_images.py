from minimongo import Index, Model
from base import BaseModel

class SimilarImage(BaseModel, Model):

    class Meta:
        database = "scrape_images"
        collection = "similar_images"

        indices = (
            Index("master"),
            Index("short_hashes")
        )
