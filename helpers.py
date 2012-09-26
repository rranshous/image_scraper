import random as r

# totally random size
bomb_size = 10

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

    def CellDamage(cell_index):
        return _signal('%s-%s:damage' % (blog_key, cell_index))

    bomb_center = page_number
    bomb_front_edge = bomb_center - bomb_size * 2
    bomb_back_edge = bomb_center + bomb_size * 2

    # the center is damanged the worst
    bomb_centers_damage = bomb_size * 2 + 1

    # go through all the pages damadged in the bombing
    for cell_index in xrange(bomb_front_edge, bomb_back_edge+1):

        # the closer to the center, the more destruction
        blast_strength = bomb_centers_damage - ( bomb_center - cell_index)

        # update the cell's damage count
        cell_damage = CellDamage(cell_index)
        cell_damage.incr(blast_strength)

    # we are keeping track of the last which took damage, if the edge
    # of this bomb is greater than the currently farthest edge update
    farthest_bombed_cell = _signal('%s:farthest_damaged_cell' % blog_key)
    if farthest_bombed_cell.value < bomb_center:
        farthest_bombed_call.value = bomb_center

    return bomb_size
