from datetime import datetime
from minimongo import Model

class BaseModel():

    def __getattr__(self, attr):
        """
        over write getattr to return None when
        we try and get the value of a non-existant
        attr rather than throwing an exception
        """

        try:
            return super(Model, self).__getattr__(attr)
        except AttributeError:
            return None

    @classmethod
    def get_one(cls, **kwargs):
        """
        convenience function to find_one
        """
        return cls.collection.find_one(kwargs)

    @classmethod
    def get_or_create(cls, **kwargs):
        """
        returns the obj matched by the passed kwargs
        or creates a new Obj and sets kwargs
        """

        obj = cls.collection.find_one(kwargs)
        if not obj:
            obj = cls(**kwargs)

            # each new object gets a created_at
            obj.created_at = datetime.now()

        return obj

