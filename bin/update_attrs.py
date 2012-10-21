"""
goes through all the records we have for images / blogs / users
setting missing attrs based on existing
"""

from multiprocessing.pool import ThreadPool

# TODO: set vhash on each image
# TODO: set created_at on each image
# TODO: set created_at on each blog

# updating path to be root of project
from os.path import dirname, abspath
import sys
print 'adding: %s' % dirname(abspath('.'))
sys.path.insert(0, abspath('.'))

# bring in the global context
from context import context

# we default to production
debug = 'debug' in sys.argv
print 'debug: %s' % debug

# set our config into the context
config = context.get('get_config')(debug, 'update_attrs')
context.add('config', config)

# compute each images vhash
compute = context.get('compute_vhash')
get_Image = context.get('get_Image')
images = get_Image().collection.find({'vhash': None,
                                      'downloaded': True})

# start up a worker pool
pool = ThreadPool(5)

def do_vhash(i, image):
    print ('\n[compute vhash] (%s/%s)\t%s' % (
                i, total_images-i, image.short_hash)),
    image_data = context.create_partial(image.get_data)()
    try:
        image.vhash = str(compute(image_data))
        print '\t' + image.vhash
        image.save()
    except Exception, ex:
        print '\n%s:: %s' % (image.short_hash, ex)
    return image.vhash

total_images = images.count()
print 'image count: %s' % total_images

step = 1001
current = 0
while images.count() > 0:
    images = get_Image().collection.find({'vhash': None,
                                          'downloaded': True})
    for image in images.limit(step):
        current += 1
        #do_vhash(i, image)
        r = pool.apply_async(do_vhash, (current,image))

