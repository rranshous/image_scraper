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

    def __getattr__(self, attr):
        """
        over write getattr to return None when
        we try and get the value of a non-existant
        attr rather than throwing an exception
        """

        try:
            return super(Image, self).__getattr__(attr)
        except AttributeError:
            return None

    @classmethod
    def get_one(cls, **kwargs):
        return cls.collection.find_one(kwargs)

    @classmethod
    def get_or_create(cls, **kwargs):
        """
        returns the Image matched by it's URL
        or creates a new Image and sets URL
        """

        obj = cls.collection.find_one(kwargs)
        if not obj:
            obj = cls(**kwargs)
        return obj

    def set_data(self, data, short_hash, upload_image):
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


    def get_data(self, data, retrieve_image):
        """
        gets the image's data
        """

        # reads the image's data and returns
        return retrieve_image(self.short_hash)
