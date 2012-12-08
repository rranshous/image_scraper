
import itertools
import os.path
from os.path import dirname, abspath
import sys

from threading import Thread, Event
from Queue import Queue, Empty

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

# gimmie a prefix to check, if ALL is provided we'll
# page through all results
prefix = sys.argv[1]

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

def downloader(download_queue, download_image, stopper):
    """ download objs from queue """
    while not stopper.is_set():
        try:
            obj = download_queue.get(True, 5)
            print 'queue obj: %s' % obj
            path = download_image(obj)
            if path:
                print path
        except Empty:
            print 'empty download queue'
        except Exception, ex:
            print 'Exception: %s' % ex


def finder(prefix_queue, _iter_cloudfile_images, stopper, download_queue):

    while not stopper.is_set():
        try:
            prefix = prefix_queue.get(True, 30)
            print 'queue prefix: %s' % prefix

            for i, obj in enumerate(_iter_cloudfile_images(prefix=prefix)):
                if stopper.is_set():
                    return
                print 'putting in queue: %s %s' % (i, obj)
                download_queue.put(obj, True, 30)
        except Empty:
            print 'empty find queue'
        except Exception, ex:
            print 'Exception: %s' % ex

DOWNLOADER_COUNT = 3
FINDER_COUNT = 5
finder_threads = set()
downloader_threads = set()
download_queue = Queue(25)
prefix_queue = Queue()
stopper = Event()
context.update(download_queue=download_queue,
               prefix_queue=prefix_queue,
               stopper=stopper)

try:

    # the downloaders
    for i in xrange(DOWNLOADER_COUNT):
        # create and start our threads
        downloader_thread = Thread(target=context.create_partial(downloader))
        downloader_thread.start()
        downloader_threads.add(downloader_thread)

    # and the finders
    for i in xrange(FINDER_COUNT):
        # create and start our threads
        finder_thread = Thread(target=context.create_partial(finder))
        finder_thread.start()
        finder_threads.add(finder_thread)

    if prefix == 'ALL':
        print 'Downloading all objects'
        for prefix in itertools.combinations('abcdef0123456789', 3):
            if context.stopper.is_set():
                break
            # go through each of the objects downloading them locally
            prefix = ''.join(prefix) # prefix will be a tuple from the combinations call
            prefix_queue.put(prefix)

    else:
        prefix_queue.put(prefix)


    # can't kill, need to work on that
    for downloader_thread in downloader_threads:
        downloader_thread.join()
    print 'DONE DOWNLOADING'
    stopper.set()
    for finder_thread in finder_threads:
        finder_thread.join()

except (Exception, KeyboardInterrupt):
    print 'stopping'
    # can't kill, need to work on that
    for downloader_thread in downloader_threads:
        downloader_thread.join()
    print 'DONE DOWNLOADING'
    stopper.set()
    for finder_thread in finder_threads:
        finder_thread.join()

