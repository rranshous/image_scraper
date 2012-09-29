from bs4 import BeautifulSoup as BS
import requests
from itertools import imap
from operator import itemgetter

from helpers import CellDamage, max_cell_damage, generate_page_url

proxies = {}
proxies = {'http':'127.0.0.1:3128'}

min_image_size = 200
min_recheck_wait = 60 * 10

def _get_html(page_url):
    try:
        return requests.get(page_url, proxies=proxies).text
    except:
        return None


def scrape_images(blog_url, page_number, page_url, _stop, _string):
    """
    yields up the src for all images on page
    """

    # pull down the html
    page_html = _get_html(page_url)

    # if we recently tried to download content from this url
    # than skip
    recently_downloaded = _string('%s:recently_downloaded' % page_url)
    if recently_downloaded.exists:
        # if the flag exists than we recently downloaded it, skip
        print 'page was recently downloaded, skipping download [%s]' % page_url
        yield False
        _stop()

    print 'page html [%s]: %s' % (page_url, len(page_html or ''))

    if not page_html:

        print 'no html: %s' % page_url

        # skip event
        yield False

    else:

        # update that it's been recently downloaded
        recently_downloaded.value = 1
        recently_downloaded.let_expire(min_recheck_wait)

        # grab our html and yield up the image source urls
        soup = BS(page_html)
        for src in imap(itemgetter('src'), soup.find_all('img')):
            yield 'image_url', src

def investigate_bombed_cells(blog_url, blog_key, page_number,
                             bomb_center, damaged_cells, _signal):
    """
    check out all the damaged cells, if any of them have passed
    their damage threshold than announce
    """

    for cell_index in damaged_cells:
        # skip the center cell
        if bomb_center == cell_index:
            continue

        cell_damage = CellDamage(_signal, blog_key, cell_index)
        print 'cell_damage [%s]: %s' % (cell_index, cell_damage.value)
        if cell_damage.value > max_cell_damage:
            yield dict( cell_damage = cell_damage.value,
                        cell_index = cell_index,
                        blog_url = blog_url,
                        blog_key = blog_key,
                        page_url = generate_page_url(blog_url, cell_index),
                        page_number = cell_index )
            cell_damage.reset()
