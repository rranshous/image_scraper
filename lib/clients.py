import os

class SafeClientContainer(object):
    """
    will create / share a client safely.
    will return a diff client for each proc / thread
    """

    def __init__(self, client_constructor):
        self.client_constructor = client_constructor

        # lookup broken down by proc + thread
        self.client_lookup = {}

    def get_client(self, *args, **kwargs):

        # who are we ?
        proc_id = os.getpid()
        thread_id = threading.current_thread().ident

        # next lvl
        threads = self.client_lookup.setdefault(proc_id, {})

        # if we don't have a client for this proc / thread
        # than lets create one
        if thread_id not in threads:
            c = self.client_constructor(*args, **kwargs)
            threads[thread_id] = c

        # return their client
        return threads[thread_id]


class get_client(object):
    def __call__(self, *args, **kwargs):
        return self.client_container.get_client(*args, **kwargs)


class get_revent_client(get_client):
    def __init__(self):
        from helpers.revent.lua_client import RedisClient
        self.client_container = SafeClientContainer(RedisClient)


class get_mongo_client(get_client):
    def __init__(self):
        from mongo import Client
        self.client_container = SafeClientContainer(Client)


class get_redis_client(get_client):
    def __init__(self):
        from redis import RedisClient
        self.client_container = SafeClientContainer(RedisClient)
