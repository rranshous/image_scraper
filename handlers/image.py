
def filter_bad(blog_url, page_url, image_url, _string,
               image_size_from_url, now, config,
               short_hash, Blog, Image, _stop):
    """
    filter: True for images which interest us

    bases decision on image size and url
    """

    # get the image's size
    image_size = image_size_from_url()
    min_image_size = config.get('image_details', {}).get('min_image_size')

    # see if we already have it's record in mongo
    image = Image().get_or_create(url=image_url)

    # if it's an avatar image, we don't want it
    if 'avatar' in image_url:
        yield False

    # ignore google ad shit
    elif 'google' in image_url:
        yield False

    # image must have size
    elif not image_size:
        yield False

    # we dont want small images
    elif image_size and image_size < min_image_size:
        yield False

    # looks like we'd save this image
    else:
        print 'good image: %s' % image_url

        # update the image's dimensions if they are not set
        if not image.dimension_long_size and image_size:
            image.dimension_long_size = image_size

        # make sure we have a blog dict to check / add to
        if not image.blogs:
            image.blogs = {}

        # create our blog document if it doesn't exist
        # TODO: set the short hash when url is set ?
        blog = Blog().get_or_create(url=blog_url)
        if not blog.short_hash:
            blog.short_hash = short_hash(blog_url)
            blog.save()

        # if this blog url isn't in the list of blogs the image
        # has been found on, add it
        if blog_url not in image.blogs.keys():
            image.blogs[blog.short_hash] = now()

        image.save()

        # if we've already downloaded the image, skip it
        if image.downloaded:
            print 'Already downloaded: skipping'
            yield False

        else:
            # push the event on
            yield 'image_size', image_size


def save(blog_url, page_url, page_number,
         image_url, upload_image, get_data, bomb, config,
         short_hash, Image, _signal, _string, _stop,
         context):
    """
    saves the image to the disk, if not already present
    """

    # see if we already downloaded the image
    image = Image().get_or_create(url=image_url)

    # if we've already downloaded the image, skip it
    # this assumes that the same image re-blogged from a different
    # blog ends up w/ a diff url
    if image and image.downloaded:
        print 'Already downloaded: skipping'
        yield False
        _stop()

    # download the image's data
    image_data = get_data(image_url)

    # if there is no image data, we're done
    if not image_data:

        print 'cant save no image data'
        yield False

    else:

        # set our image's data, lean on the context for missing args
        storage_key = context.create_partial(image.set_data)(image_data)
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

