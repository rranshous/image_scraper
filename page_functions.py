from bs4 import BeautifulSoup as BS
import requests
from itertools import imap
from operator import itemgetter

proxies = {'http':'127.0.0.1:3128'}
min_image_size = 200

def get_html(page_url):
    """
    yields HTML or None for page's url
    """

    try:
        yield 'page_html', requests.get(page_url, proxies=proxies).text
    except:
        yield None


def scrape_images(page_html):
    """
    yields up the src for all images on page
    """

    # if we didn't get the html, we're done
    if not page_html:
        yield False

    else:
        # grab our html and yield up the image source urls
        soup = BS(page_html)
        for src in imap(itemgetter('src'), soup.find_all('img')):
            yield 'image_url', src


def filter_seen(page_url):
    """
    filter: True for page url's which we should scrape

    bases decision on last logged bad page url
    """

    # TODO
    yield True

