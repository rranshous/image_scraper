

from lib.config import get_config
from lib.bubbles import build_context
import lib.helpers as h
import lib.clients as c
import objects as o
import datetime

# set up the base mapping for our central context

base_map = dict(

    # CLIENTS

    revent = c.get_revent_client,
    mongo = c.get_mongo_client,
    redis = c.get_redis_client,

    # HELPERS

    upload_image = h.upload_image,
    get_html = h.get_html,
    get_data = h.get_data,
    save_new_image = h.upload_image,
    get_saved_image = h.retrieve_image,
    get_image_public_url = h.get_image_public_url,
    bomb = h.bomb,
    short_hash = h.short_hash,
    CellDamage = h.CellDamage,
    generate_page_url = h.generate_page_url,
    image_size_from_url = h.image_size_from_url,
    get_channel_details = get_channel_details,

    # OBJECTS

    get_Image = o.get_image_object,
    get_Blog = o.get_blog_object,

    # CONFIG

    get_config = get_config

    # MISC

    now = datetime.datetime.now

    # TODO: add smart accessors like:
    #       blog_url => blog_short_hash

)

context = build_context(**base_map)
