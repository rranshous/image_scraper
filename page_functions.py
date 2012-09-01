min_image_size = 200

def scrape_page_for_images(page_url):
    """
    yields up the src for all images on page
    """

    # grab our html and yield up the image source urls
    soup = BS(get_html(page_url))
    for src in imap(itemgetter('src'), soup.find_all('img')):
        yield src


def filter_bad_images(image_url, image_size):
    """
    filter: True for images which interest us

    bases decision on image size
    """

    # if it's an avatar image, we don't want it
    if 'avatar' in image_url:
        yield False

    # we dont want small images
    elif size and size < min_image_size:
        yield False

    else:
        yield True
