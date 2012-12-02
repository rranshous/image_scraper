
## we want to associate similar images to each other

from multiprocessing.pool import ThreadPool
pool = ThreadPool(5)

from os.path import abspath, dirname, join as path_join
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

# TODO: add to config
MIN_DISTANCE = config.get('similar', 'min_distance')
MIN_DISTANCE = 5

Image = context.get('get_Image')()
SimilarImage = context.get('get_SimilarImage')()
compare_vhash = context.get('compare_vhash')

# go through each image's vhash finding
# images it's similar to other images


def do_compare(im):

    print '%s' % im.short_hash

    for im2 in Image.collection.find({'vhash':{'$exists':True}}):

        if im.short_hash == im2.short_hash:
            continue

        if im.similar_found:
            continue

        if compare_vhash(im.vhash, im2.vhash) < MIN_DISTANCE:

            print '%s=>%s' % (im.short_hash, im2.short_hash)

            # we found a similar image! lets see if that image is already
            # in a similar image document
            similar = SimilarImage.get_one(short_hashes=im2.short_hash)

            if similar:

                # if we've already got a document w/ images similar to our
                # master image than add the master image to the doc
                similar.short_hashes.append(im.short_hash)

            else:

                # there isn't a document for these images, create one
                similar = SimilarImage()
                similar.short_hashes = []
                similar.short_hashes.append(im.short_hash)
                similar.short_hashes.append(im2.short_hash)
                # default the target image to master
                similar.master = im2.short_hash

            # if the current image is larger than master, replace it
            mi = Image.get_one(short_hash=similar.master)
            if (mi.dimension_long_size or 0) < (im.dimension_long_size or 0):
                print 'setting as master'
                similar.master = im.short_hash
                for sh in similar.short_hashes:
                    if sh == im.short_hash:
                        continue
                    _im = Image.get_one(short_hash=sh)
                    _im.is_master = False
                    _im.save()

                im.is_master = True

            # update the image doc to flag we've found similar images
            im.similar_found = True
            im.save()
            im2.similar_found = True
            im2.save()

            # save our similar doc
            similar.save()


while True:
    step = 10
    dissimilar_images = Image.collection.find({
                            'vhash': {'$exists': True},
                            'similar_found': {'$ne': True}
                        }).limit(step)

    for im in dissimilar_images:
        do_compare(im)

    """
    results = []
    for im in dissimilar_images:
        r = pool.apply_async(do_compare, (im,))

    # wait for all results
    for r in results:
        r.get()
    """
