from minimongo import Model, Index

class Image(Model):
    class Meta:
        # Here, we specify the database and collection names.
        # A connection to your DB is automatically created.
        database = "scrape_images"
        collection = "images"

        # Now, we programatically declare what indices we want.
        # The arguments to the Index constructor are identical to
        # the args to pymongo"s ensure_index function.
        indices = (
            Index("url"),
            Index("short_hash")
        )

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


def filter_bad(blog_url, page_url, image_url, _string, _stop,
               Image, config):
    """
    filter: True for images which interest us

    bases decision on image size and url
    """

    # if we recently tried to download content from this url
    # than skip
    recently_downloaded = _string('%s:recently_downloaded' % image_url)
    if recently_downloaded.exists:
        # if the flag exists than we recently downloaded it, skip
        print 'image was recently downloaded, skipping download [%s]' % image_url
        yield False
        _stop()

    # get the image's size
    image_size = get_image_size(blog_url, page_url, image_url)
    min_image_size = config.get('image_details', {}).get('min_image_size')

    # see if we already have it's record in mongo
    image = Image.find_one({ 'image_url': image_url })

    # if we've already downloaded the image, skip it
    if image.downloaded:
        yield False

    # if it's an avatar image, we don't want it
    if 'avatar' in image_url:
        yield False

    # ignore google ad shit
    if 'google' in image_url:
        yield False

    # image must have size
    elif not image_size:
        yield False

    # we dont want small images
    elif image_size and image_size < min_image_size:
        yield False

    else:
        print 'good image: %s' % image_url
        yield 'image_size', image_size


def save(blog_url, blog_key, page_url, page_number,
         image_url, upload_image, get_data, bomb,
         _signal, _string, _stop):
    """
    saves the image to the disk, if not already present
    """

    # if we recently tried to download content from this url
    # than skip
    recently_downloaded = _string('%s:recently_downloaded' % sh(image_url))
    if recently_downloaded.exists:
        # if the flag exists than we recently downloaded it, skip
        print 'image was recently downloaded, skipping download [%s]' % image_url
        yield False
        _stop()

    # download the image's data
    image_data = get_data(image_url)

    # if there is no image data, we're done
    if not image_data:
        print 'cant save no image data'
        yield False

    else:

        # upload our image
        image_hash = upload_image(image_data)

        # did we upload the image ?
        if image_hash is not False:

            print 'saved: %s' % image_hash

            # if we were uploaded than put off our saved event
            yield dict( blog_url=blog_url,
                        blog_key=blog_key,
                        page_number=page_number,
                        page_url=page_url,
                        save_path=image_hash,
                        image_hash=image_hash,
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
            print 'no save: %s' % (image_url)

    # update that it's been recently downloaded
    recently_downloaded.value = 1
    if min_recheck_wait:
        recently_downloaded.let_expire(min_recheck_wait)

