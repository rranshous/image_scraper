import os, threading

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


from lib.revent.lua_client import RedisClient as ReventClient
get_revent_client = SafeClientContainer(ReventClient).get_client

from pymongo import Connection as MConnection
get_mongo_client = SafeClientContainer(MConnection).get_client

from redis import Redis
get_redis_client = SafeClientContainer(Redis).get_client

