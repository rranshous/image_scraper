from hashlib import sha1
import os.path
import cloudfiles


def CellDamage(cell_index, blog_url, short_hash, _signal):
    blog_key = short_hash(blog_url)
    return _signal('%s-%s:damage' % (blog_key, cell_index))


def get_city_size(blog_url, short_hash, _signal):
    """
    returns the estimated size of the city (blog)
    """

    # we are going to estimate the size of the city
    # by looking for the farthest away cell which has
    # taken damage
    blog_key = short_hash(blog_url)
    farthest_bombed_cell = _signal('%s:farthest_damaged_cell' % blog_key)
    return farthest_bombed_cell


def bomb(page_number, blog_url, _signal,
         config, short_hash, CellDamage):
    """
    'bombs' a page, increasing the likelyhood that
    the bombed page and it's neightbors are scraped
    """

    # When we bomb a page we increase the page's signal
    # as well as it's neighbors

    blog_key = short_hash(blog_url)
    bomb_size = config.get('bomb').get('size')
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
        cell_damage = CellDamage(cell_index)
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


def _get_image_container(servicenet=False):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, 'rackspace_creds.txt')
    with open(path, 'r') as fh:
        creds = [x.strip() for x in fh.readlines() if x.strip()]

    conn = cloudfiles.get_connection(*creds,
                                     servicenet=servicenet)
    container = conn.get_container('scrape_images')
    return container


def upload_image(image_data, config):
    """
    uploads the image to rackspace cloud files
    """

    image_hash = short_hash(image_data)
    servicenet = config.get('cloudfiles', {}).get('servicenet')
    container = _get_image_container(servicenet)

    try:
        # check if it exists, don't want to re-upload
        obj = container.get_object(image_hash)
# if it exists return False
        return False

    except:

        # it doesn't exist yet
        obj = container.create_object(image_hash)
        obj.content_type = 'image'
        obj.write(image_data)
        return image_hash


def retrieve_image(img_short_hash, config, retries=1):
    """
    retrieves an image from rackspace cloud files by short hash
    """

    servicenet = config.get('cloudfiles', {}).get('servicenet')
    container = _get_image_container(servicenet)

    for i in xrange(retries+1):
        try:
            # check if it exists, don't want to re-upload
            obj = container.get_object(img_short_hash)
            return obj

        except:
            # if this is the last re-try, just raise
            if i == retries - 1:
                raise


def short_hash(data):
    """
    creates a short sha based hash for given data
    """

    digest = sha1()
    digest.update(data)
    key = hex(int(digest.hexdigest(), 16) % (2**41))[2:-1]
    return key


def get_html(url, config):
    """
    yields HTML or None of url
    """
    try:
        import requests
        proxies = config.get('proxies', {})
        print 'PROXIES: %s' % proxies
        return requests.get(url, proxies=proxies).text
    except:
        raise


def get_data(url, config):
    """
    yields resource data or None
    """
    try:
        import requests
        proxies = config.get('proxies', {})
        print 'PROXIES: %s' % proxies
        return requests.get(url, proxies=proxies).content
    except:
        raise

def image_size_from_url(blog_url, page_url, image_url):
    """
    returns an int representing the images smallest side
    """

    found_size = None
    url_patterns = ['media.tumblr.com','tumblr.com/photo']

    # see if we can get the size from the url
    for p in url_patterns:
        if p in image_url:
            size = image_url[-7:-4]
            if size.isdigit():
                found_size = int(size)
                break

    # if we didn't get it from the url, download the image
    # and inspect the image
    # TODO

    if found_size:
        return 'image_size', found_size
