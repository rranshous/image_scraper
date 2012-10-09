from minimongo import Index, Model
from base import BaseModel

class Image(BaseModel, Model):
    class Meta:
        database = "scrape_images"
        collection = "images"

        indices = (
            Index("url"),
            # TODO: figure out how to index urls in hash keys
            # Index("blog_urls"),
            Index("is_stored"),
            Index("short_hash")
        )


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
        # even if the storage key is false we are still updating
        # this flag, since it is downloaded, just already was
        self.downloaded = True

        # save the storage key
        if storage_key is not False:
            self.storage_key = storage_key

        # cheat, we know the storage key is the short_hash,
        # so lets set that
        else:
            self.storage_key = self.short_hash

        # uploaded is the name of the key if we uploaded
        # if it already existed, we get False
        return storage_key


    def get_data(self, data, retrieve_image):
        """
        gets the image's data
        """

        # reads the image's data and returns
        return retrieve_image(self.short_hash)
