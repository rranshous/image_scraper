import requests

max_blog_pages = 2000
proxies = {'http':'127.0.0.1:3128'}

def verify_url(blog_url):
    """
    filter: True if url responds with 200
    """
    try:
        r = requests.get(blog_url, proxies=proxies)
        yield True
    except Exception, ex:
        pass

def fan_out_pages(blog_url, event_data):
    """
    given the blog url generates the urls for all blog pages

    naive function which simply generates urls for pages from
    one to 2000
    """

    for i in xrange(1, max_blog_pages):
        yield 'page_url', blog_url + 'page/' + str(i)


