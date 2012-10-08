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


    @classmethod
    def get(cls, url):
        """
        returns the Image matching given URL or None
        """
        return cls.collection.find_one({'url':url})

    @classmethod
    def get_or_create(cls, url):
        """
        returns the Image matched by it's URL
        or creates a new Image and sets URL
        """

        obj = cls.collection.find_one({'url':url})
        if not obj:
            obj = cls()
            obj.url = url
        return obj

    def set_data(self, data):
        """
        stores the given data

        returns the data's store key if uploaded
        returns False if data already existed
        """

        # get the short hash for the data
        self.short_hash = short_hash(data)

        # TODO: compute other attrs: type, vhash, dimensions

        # save the data to the cloud
        storage_key = upload_image(data)

        # upload our downloaded flag
        self.downloaded = True

        # save the storage key
        self.storage_key = storage_key

        # uploaded is the name of the key if we uploaded
        # if it already existed, we get False
        return storage_key


    def get_data(self, data):
        """
        gets the image's data
        """

        # reads the image's data and returns
        return retrieve_image(self.short_hash)
