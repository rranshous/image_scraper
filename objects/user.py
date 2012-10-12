
from minimongo import Index, Model
from base import BaseModel

class User(BaseModel, Model):
    class Meta:
        database = "scrape_images"
        collection = "users"

        indices = (
            Index("handle"),
            Index("category_ratings"),
        )

    # mark favorite image
    # like image
    # dislike image

    def _mark_image_preference(self, image_short_hash, preference_type,
                               weight, Image):
        """
        helper function which marks the users preference toward the image
        and gives the images categories weight for the user
        """

        # get our image
        image = Image.get_one(short_hash=image_short_hash)
        assert image, "Could not find image"

        # make sure this preference type's attributes exist
        pref_attr = '%s_images' % preference_type
        if not getattr(self, pref_attr, None):
            setattr(self, pref_attr, [])

        if not image_short_hash in getattr(self, pref_attr):
            getattr(self, pref_attr).append(image_short_hash)

        # create our category ratings lookup if it's not already set
        self.category_ratings = self.category_ratings or {}

        # update our inferred category likes using the cats on
        # the image
        for category in image.categories or []:

            # keep all cats as lowercase
            category = category.lower()

            # update the preference weight
            if category in self.category_ratings:
                self.category_ratings[category] += weight
            else:
                self.category_ratings[category] = weight

        return True

    def like_image(self, image_short_hash, Image):
        """
        marks the image who's hash we're passed as being liked
        by the user
        """

        return self._mark_image_preference(image_short_hash,
                                           'like', 1,
                                           Image)


    def favorite_image(self, image_short_hash, Image):
        """
        marks the image who's hash we're passed as being a favorite
        of the user
        """

        return self._mark_image_preference(image_short_hash,
                                           'favorite', 2,
                                           Image)


    def dislike_image(self, image_short_hash, Image):
        """
        marks the image who's hash we're passed as being disliked
        by the user
        """

        return self._mark_image_preference(image_short_hash,
                                           'dislike', -1,
                                           Image)

