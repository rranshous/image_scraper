from minimongo import Index, Model
from base import BaseModel
from datetime import datetime

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


    def set_data(self, data, short_hash, upload_image, Blog, blog_url=None):
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

        # if they told us the blog, make sure we stored it
        if blog_url:

            # create our blog document if it doesn't exist
            # TODO: set the short hash when url is set ?
            blog = Blog().get_or_create(url=blog_url)
            if not blog.short_hash:
                blog.short_hash = short_hash(blog_url)
                blog.save()

            self.blog_urls = self.blog_urls or {}
            if blog.short_hash not in self.blog_urls:
                self.blog_urls[blog.short_hash] = datetime.now()

        # uploaded is the name of the key if we uploaded
        # if it already existed, we get False
        return storage_key


    def get_data(self, data, retrieve_image):
        """
        gets the image's data
        """

        # reads the image's data and returns
        return retrieve_image(self.short_hash)
