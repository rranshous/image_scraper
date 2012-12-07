
import itertools
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
def download_image(obj, out_path, overwrite=False):
    out_p = os.path.join(out_path, obj.name)
    if os.path.exists(out_p) and not overwrite:
        return False
    obj.save_to_filename(out_p)
    return out_p

# add our helpers to the context
context.update(download_image=download_image)

# if we have a prefix of 'ALL' than we want to try and download
# all the images, the problem is there is a 9999 item limit
# to paging through the cloudfiles container, to get around
# this we are going to use 3 letter prefixes, trying every combination
# of 3 letter / number

if context.prefix == 'ALL':
    print 'Downloading all objects'
    for prefix in itertools.combinations('abcdefghijklmnopqrstuvwxyz0123456789', 3):
        # go through each of the objects downloading them locally
        for i, obj in enumerate(context._iter_cloudfile_images(prefix=prefix)):
            img_path = context.download_image(obj)
            if img_path:
                print '[%s] %s' % (i, img_path)

# normal, non-all run
else:
    # go through each of the objects downloading them locally
    for i, obj in enumerate(context._iter_cloudfile_images()):
        img_path = context.download_image(obj)
        if img_path:
            print '[%s] %s' % (i, img_path)


