from bs4 import BeautifulSoup as BS
import requests
from itertools import imap
from operator import itemgetter

proxies = {'http':'127.0.0.1:3128'}
proxies = {}
min_image_size = 200

def _get_html(page_url):
    try:
        return requests.get(page_url, proxies=proxies).text
    except:
        return None


def scrape_images(blog_url, page_url, _do_work):
    """
    yields up the src for all images on page
    """

    # see if it suggests we do the work
    do_work, confirm = _do_work(page_url)

    # if it doesn't suggest we do the work, than lets not
    if not do_work:
        _stop()

    # pull down the html
    page_html = _get_html(page_url)

    if not page_html:

        # work did not work out
        confirm(False)

        # skip event
        yield False

    else:

        # work was good
        confirm(True)

        # grab our html and yield up the image source urls
        soup = BS(page_html)
        for src in imap(itemgetter('src'), soup.find_all('img')):
            yield 'image_url', src


