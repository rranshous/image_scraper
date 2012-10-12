from minimongo import Index, Model
from base import BaseModel
from datetime import datetime

class Image(BaseModel, Model):
    class Meta:
        database = "scrape_images"
        collection = "images"

        indices = (
            Index("url"),
            Index("blogs"),
            Index("downloaded"),
            Index("short_hash"),
            Index("categories")
        )


    def mark_seen(self, short_hash, blog_url, Blog, Image, seen_at=None):
        """
        Marks the image as having been seen on the given blog
        """

        # get the image we just saw
        image = Image.get_one(short_hash=short_hash)
        assert image, "Could not find image to mark seen"

        # get the blog where we just saw this image
        blog = Blog().get_or_create(url=blog_url)

        # update the blog new blog obj's short hash
        if not blog.short_hash:
            blog.short_hash = short_hash(blog_url)
            blog.save()

        assert blog, "Could not find blog to mark image seen"

        # check if the image already has the blog's reference
        if blog.short_hash not in image.blogs:

            # if they didn't specify when they saw it, assume now
            seen_at = seen_at or datetime.now()

            # add the blog in as being seen
            image.blogs[blog.short_hash] = seen_at

        # add the blog's categories as the images
        for category in blog.categories:
            if category not in self.categories:
                self.categories.append(category.lower())

        # return our timestamp
        return seen_at


    def set_data(self, data, short_hash, upload_image,
                 Blog, Image, blog_url=None):
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

        # when did we get it's data ?
        if storage_key is not False:
            self.last_data_set = datetime.now()

        # save the storage key
        if storage_key is not False:
            self.storage_key = storage_key

        # cheat, we know the storage key is the short_hash,
        # so lets set that
        elif not self.storage_key:
            self.storage_key = self.short_hash

        # if they told us the blog, make sure we stored it
        if blog_url:
            self.mark_seen(short_hash, blog_url, Blog, Image)

        # uploaded is the name of the key if we uploaded
        # if it already existed, we get False
        return storage_key


    def get_data(self, retrieve_image, stream=False):
        """
        gets the image's data
        """

        # reads the image's data and returns
        return retrieve_image(self.short_hash,
                              stream=stream)


    def get_public_url(self, get_image_public_url):
        """
        returns a public url for this image
        """

        # get that url
        return get_image_public_url(self.short_hash)

