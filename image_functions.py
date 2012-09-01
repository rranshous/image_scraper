from os.path import abspath, exists

save_root = abspath('./output')

def get_image_size(image_url):
    """
    returns an int representing the images smallest side
    """

    size = None

    # see if we can get the size from the url
    for p in url_patterns:
        if p in image_url:
            size = image_url[-7:-4]
            if size.isdigit() and int(size) > min_img_size:
                size = int(size)
                break

    # if we didn't get it from the url, download the image
    # and inspect the image
    # TODO

    yield size

def _get_save_path(image_url, image_data):
    # save our images under it's sha
    return join(save_root, sha1(image_data).hexdigest())

def filter_seen_images(image_url, image_size):
    """
    filter: True if we haven't already downloaded image
    """

    return True

    # TODO: check redis for the url
    yield image_url in downloaded_images


def save_image(image_url, image_size, image_data):
    """
    saves the image to the disk, if not already present
    """

    save_path = _get_save_path(image_url, image_data)

    # don't bother re-saving
    if not exists(save_path):

        with open(save_path, 'rb') as fh:
            fh.write(image_data)

        yield save_path
