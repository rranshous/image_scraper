"""
goes through all the records we have for images / blogs / users
setting missing attrs based on existing
"""

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

print 'image count: %s' % images.count()
for image in images:
    print ('[compute vhash] %s' % image.short_hash),
    image_data = context.create_partial(image.get_data)()
    image.vhash = str(compute(image_data))
    print image.vhash
    image.save()

