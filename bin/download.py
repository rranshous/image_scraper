

import cloudfiles
import os.path
from os.path import dirname, abspath
import sys

# what dir is this file in ?
here = dirname(abspath(__file__))

# update our python path to be at root of project
base = dirname(here)
sys.path.insert(0, base)

# we default to production
debug = 'debug' in sys.argv
print 'debug: %s' % debug

# CONTEXT
from context import context

# set our config into the context
config = context.get('get_config')(debug, 'scraper')
context.add('config', config)

# gimmie a prefix to check, if none is provided we'll
# page through all results
context.update(prefox=sys.argv[1])

# what dir are these files going into ?
context.update(out_path=os.path.abspath(sys.argv[2]))

# our functions to do the work
def download_image(obj, out_path):
    out_p = os.path.join(out_path, obj.name)
    print out_p
    obj.save_to_filename(out_p)

# add our helpers to the context
context.update(download_image=download_image)

# go through each of the objects downloading them locally
for i, obj in enumerate(context._iter_cloudfile_images()):
    print '[%s] '%i
    context.download_image(obj)


