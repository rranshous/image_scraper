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


def scrape_images(blog_url, page_url, _stop):
    """
    yields up the src for all images on page
    """

    # pull down the html
    page_html = _get_html(page_url)

    if not page_html:

        # skip event
        yield False

    else:

        # grab our html and yield up the image source urls
        soup = BS(page_html)
        for src in imap(itemgetter('src'), soup.find_all('img')):
            yield 'image_url', src


