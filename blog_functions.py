max_blog_pages = 2000

def fan_out_blog_pages(blog_url):
    """
    given the blog url generates the urls for all blog pages

    naive function which simply generates urls for pages from
    one to 2000
    """

    for i in xrange(1, max_blog_pages):
        yield blog_url + 'page/' + str(i)


def filter_seen_pages(page_url):
    """
    filter: True for page url's which we should scrape

    bases decision on last logged bad page url
    """

    return True

    # TODO
    return page_url in bad_blog_pages

