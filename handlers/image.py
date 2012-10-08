
def filter_bad(blog_url, page_url, image_url, _string, _stop,
               image_size_from_url, Image, config):
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
    image_size = image_size_from_url()
    min_image_size = config.get('image_details', {}).get('min_image_size')

    # see if we already have it's record in mongo
    image = Image.get_or_create(image_url)

    # update the image's dimensions if they are not set
    if not image.dimension_long_side:
        image.dimension_long_size = image_size
        image.save()

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


def save(blog_url, page_url, page_number,
         image_url, upload_image, get_data, bomb, config,
         short_hash, Image, _signal, _string, _stop):
    """
    saves the image to the disk, if not already present
    """

    # if we recently tried to download content from this url
    # than skip
    recently_downloaded = _string('%s:recently_downloaded' %
                                  short_hash(image_url))

    if recently_downloaded.exists:

        # if the flag exists than we recently downloaded it, skip
        print 'image was recently downloaded, skipping download [%s]' % image_url
        yield False
        _stop()

    # see if we already downloaded the image
    image = Image.get(image_url)

    # if we've already downloaded the image, skip it
    if image and image.downloaded:
        yield False

    # download the image's data
    image_data = get_data(image_url)

    # if there is no image data, we're done
    if not image_data:

        print 'cant save no image data'
        yield False

    else:

        # see if this is the first time we've seen this image
        new_image = not image

        # is this the first time we've seen this image?
        # we could have seen it before but not downloaded it
        if new_image:

            # create our image obj if it's a new image
            image = Image.get_or_create(image_url)

            # let the image know what blog we found it on
            image.blog_url = blog_url

            # save our image obj's changes
            image.save()

            # put off event that we found a new image
            yield 'new_image', dict( blog_url=blog_url,
                                     page_number=page_number,
                                     image_url=image_url )

        # set our image's data
        storage_key = image.set_data(image_data)

        # save our changes to the image
        image.save()

        # did we upload the image ?
        if storage_key is not False:

            print 'saved: %s' % storage_key

            # if we were uploaded than put off our saved event
            yield dict( blog_url=blog_url,
                        page_number=page_number,
                        page_url=page_url,
                        storage_key=storage_key,
                        image_hash=image.short_hash,
                        image_url=image_url )

            # bomb the page !
            bomb_size, bomb_center, damaged_cells = bomb()

            # let the world know
            yield 'cell_bombed', dict( blog_url = blog_url,
                                       page_url = page_url,
                                       page_number = page_number,
                                       bomb_size = bomb_size,
                                       damaged_cells = damaged_cells,
                                       bomb_center = bomb_center )

        else:
            print 'no save: %s' % (image_url)

    # update that it's been recently downloaded
    recently_downloaded.value = 1

    # if there is a min time period we wait between re-downloads
    # update the flag to expire @ that offset
    min_recheck_wait = config.get('image_details').get('min_recheck_wait')
    if min_recheck_wait:
        recently_downloaded.let_expire(min_recheck_wait)

