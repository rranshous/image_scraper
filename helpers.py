import random as r
from hashlib import sha1
import os.path
import cloudfiles

here = os.path.dirname(os.path.abspath(__file__))
# totally random size
bomb_size = 2
max_cell_damage = bomb_size * 2 + 1

def CellDamage(_signal, blog_key, cell_index):
    return _signal('%s-%s:damage' % (blog_key, cell_index))


def get_city_size(_signal, blog_key):
    """
    returns the estimated size of the city (blog)
    """

    # we are going to estimate the size of the city
    # by looking for the farthest away cell which has
    # taken damage

    farthest_bombed_cell = _signal('%s:farthest_damaged_cell' % blog_key)
    return farthest_bombed_cell


def bomb(_signal, blog_key, page_number):
    """
    'bombs' a page, increasing the likelyhood that
    the bombed page and it's neightbors are scraped
    """

    # When we bomb a page we increase the page's signal
    # as well as it's neighbors

    bomb_center = page_number
    bomb_front_edge = bomb_center - bomb_size * 2
    bomb_back_edge = bomb_center + bomb_size * 2
    # there aren't negative cells
    bomb_front_edge = max(bomb_front_edge, 0)

    # the center is damanged the worst
    bomb_centers_damage = bomb_size * 2 + 1

    # go through all the pages damadged in the bombing
    damaged_cells = []
    for cell_index in xrange(bomb_front_edge, bomb_back_edge+1):

        # the closer to the center, the more destruction
        blast_strength = bomb_centers_damage - ( bomb_center - cell_index)

        # update the cell's damage count
        cell_damage = CellDamage(_signal, blog_key, cell_index)
        cell_damage.incr(blast_strength)

        damaged_cells.append(cell_index)

    # we are keeping track of the last which took damage, if the edge
    # of this bomb is greater than the currently farthest edge update
    farthest_bombed_cell = _signal('%s:farthest_damaged_cell' % blog_key)
    if farthest_bombed_cell.value < bomb_center:
        farthest_bombed_cell.value = bomb_center

    return bomb_size, bomb_center, damaged_cells


def generate_page_url(blog_url, page_number):
    if blog_url.endswith('/'):
        return '%spage/%s' % (blog_url, page_number)
    else:
        return '%s/page/%s' % (blog_url, page_number)

def upload_image(image_data, sha1_hash=None):
    """
    uploads the image to rackspace cloud files
    """

    path = os.path.join(here, 'rackspace_creds.txt')
    with open(path, 'r') as fh:
        creds = [x.strip() for x in fh.readlines() if x.strip()]

    # clac the sha1 if it's not given
    if not sha1_hash:
        sha1_hash = sha1(image_data).hexdigest()

    conn = cloudfiles.get_connection(*creds, servicenet=True)
    container = conn.get_container('scrape_images')

    try:
        # check if it exists, don't want to re-upload
        obj = container.get_object(sha1_hash)

        # if it exists return False
        return False
    except:

        # it doesn't exist yet
        obj = container.create_object(sha1_hash)
        obj.content_type = 'image'
        obj.write(image_data)
        return sha1_hash

