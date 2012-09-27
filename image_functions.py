from os.path import abspath, exists, join
from hashlib import sha1
import requests
from base64 import b64encode, b64decode

from helpers import bomb

save_root = abspath('./output')
proxies = {}
proxies = {'http':'127.0.0.1:3128'}
min_image_size = 200

def get_image_size(blog_url, page_url, image_url):
    """
    returns an int representing the images smallest side
    """

    found_size = None
    url_patterns = ['media.tumblr.com','tumblr.com/photo']

    # see if we can get the size from the url
    for p in url_patterns:
        if p in image_url:
            size = image_url[-7:-4]
            if size.isdigit():
                found_size = int(size)
                break

    # if we didn't get it from the url, download the image
    # and inspect the image
    # TODO

    if found_size:
        return 'image_size', found_size


def filter_bad(blog_url, page_url, image_url, _stop):
    """
    filter: True for images which interest us

    bases decision on image size and url
    """

    # get the image's size
    image_size = get_image_size(blog_url, page_url, image_url)

    # if it's an avatar image, we don't want it
    if 'avatar' in image_url:
        yield False

    # ignore google ad shit
    if 'google' in image_url:
        yield False

    # we dont want small images
    elif image_size and image_size < min_image_size:
        yield False

    else:
        print 'good image: %s' % image_url
        yield 'image_size', image_size


def _get_save_path(image_url, image_data):
    # save our images under it's sha
    return join(save_root, sha1(image_data).hexdigest())


def _get_data(image_url):
    try:
        return requests.get(image_url, proxies=proxies).content
    except Exception:
        return None

def save(blog_url, blog_key, page_url, page_number,
         image_url, _signal):
    """
    saves the image to the disk, if not already present
    """

    # download the image's data
    image_data = _get_data(image_url)

    # if there is no image data, we're done
    if not image_data:
        print 'cant save no image data'
        yield False

    else:

        # figure out where on the disk to save, abspath
        save_path = _get_save_path(image_url, image_data)

        # don't bother re-saving
        if not exists(save_path):

            print 'save: %s %s' % (image_url, save_path)
            with open(save_path, 'wb') as fh:
                fh.write(image_data)

            yield dict( blog_url=blog_url,
                        blog_key=blog_key,
                        page_number=page_number,
                        page_url=page_url,
                        save_path=save_path,
                        image_url=image_url )

            # bomb the page !
            bomb_size, bomb_center, damaged_cells = bomb(_signal,
                                                          blog_key,
                                                          page_number)

            # let the world know
            yield 'cell_bombed', dict( blog_url = blog_url,
                                       blog_key = blog_key,
                                       page_url = page_url,
                                       page_number = page_number,
                                       bomb_size = bomb_size,
                                       damaged_cells = damaged_cells,
                                       bomb_center = bomb_center )

        else:
            print 'no save: %s %s' % (image_url, save_path)
