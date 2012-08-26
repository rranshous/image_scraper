"""
finds images which we might want on tumblr
"""

# read in our config

# our global stop event for all work
stop_event = Event()

# we're going to use revent to keep our state, all our state
# changes will be sent as events which we will than consume


def handle_timer_scrape_blog(blog_name=None, blog_url=None):
    """
    incoming event: timer_scrape_blog :: { blog_name, blog_url }
    action: generates an event for each possible page of the blog
    emmitted event: blog_possible_page :: { blog_name, blog_url, page_url }
    """

    # TODO: learn where the end of the blog is

    # generate all possible page urls, base events on possible pages
    for possible_page_url in get_possible_page_urls(blog_url):
        yield dict( blog_name=blog_name, blog_url=blog_url, page_url=possible_page_url )

def handle_blog_possible_page(blog_name=None, blog_url=None, page_url=None):
    """
    incoming event: blog_possible_page :: { blog_name, blog_url, page_url }
    action: generates an event if page is found valid
    emmitted event: blog_page :: { blog_name, blog_url, page_url }
    """

    # validate the page as being scrapable
    if validate_page(page_url):
        # it's valid, pass on it's info
        yield dict( blog_name=blog_name, blog_url=blog_url, page_url=page_url)

    # nothing to do if it's not valid, we're a filter

def handle_blog_page(blog_name=None, blog_url=None, page_url=None):
    """
    incoming event: handle_blog_page :: { blog_name, blog_url, page_url }
    action: scrape images on page, generating an event for each found
    emitted event: blog_image :: { blog_name, blog_url, page_url, image_url }
    """

    for image_url in scrape_page_images(page_url):
        yield dict( blog_name=blog_name,
                    blog_url=blog_url,
                    page_url=page_url,
                    image_url=image_url )

def handle_blog_image(blog_name=None, blog_url=None, page_url=None, image_url=None):
    """
    incomming event: blog_image :: { blog_name, blog_url, page_url, image_url }
    action: puts off an image found event for each blog image
    emmitted event: image_found :: { src_page, src_url }
    """

    yield dict( src_page = page_url, src_url = image_url )
