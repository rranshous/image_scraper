from minimongo import Model, Index

class Image(Model):
    class Meta:
        database = "scrape_images"
        collection = "images"

        indices = (
            Index("url"),
            Index("blog_url"),
            Index("is_stored"),
            Index("short_hash")
        )


    def set_data(self, data):
        """
        stores the given data
        """
        pass

    def get_data(self, data):
        """
        gets the image's data
        """
        pass
