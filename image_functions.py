from os.path import abspath, exists, join
from hashlib import sha1
import requests
from base64 import b64encode, b64decode

save_root = abspath('./output')
proxies = {'http':'127.0.0.1:3128'}
min_image_size = 200

def get_size(image_url):
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

    yield found_size


def filter_bad(image_url, image_size):
    """
    filter: True for images which interest us

    bases decision on image size
    """

    # if it's an avatar image, we don't want it
    if 'avatar' in image_url:
        yield False

    # we dont want small images
    elif image_size and image_size < min_image_size:
        yield False

    else:
        yield True


def _get_save_path(image_url, image_data):
    # save our images under it's sha
    return join(save_root, sha1(image_data).hexdigest())


def filter_seen(image_url, image_size):
    """
    filter: True if we haven't already downloaded image
    """

    yield True

    # TODO: check redis for the url
    #yield image_url in downloaded_images


def get_data(image_url, image_size):
    """
    yields up the image's data or None
    """

    try:
        data = requests.get(image_url, proxies=proxies).content
        # encode the data so that it's json compatible
        yield b64encode(data)
    except:
        yield None


def save(image_url, image_size, image_data):
    """
    saves the image to the disk, if not already present
    """

    # if there is no image data, we're done
    if not image_data:
        yield False

    else:

        # image data is going to be encoded
        image_data = b64decode(image_data)

        save_path = _get_save_path(image_url, image_data)

        # don't bother re-saving
        if not exists(save_path):

            with open(save_path, 'wb') as fh:
                fh.write(image_data)

            yield save_path

def broadcast_save(blog_url, page_url, page_html, image_url,
                   image_size, image_data, image_save_path):
    yield dict(blog_url=blog_url, page_url=page_url, image_url=image_url, image_size=image_size, image_save_path=image_save_path)