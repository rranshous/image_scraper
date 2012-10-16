""" scraping script """

from os.path import abspath, dirname, join as path_join
import sys
import datetime


# what dir is this file in ?
here = dirname(abspath(__file__))

# update our python path to be at root of project
base = dirname(here)
sys.path.insert(0, base)

# we default to production
debug = 'debug' in sys.argv
print 'debug: %s' % debug


# bring in the event app framework
from lib.eventapp import EventApp
import lib.eventapp as eventapp


# bring in the event handler functions
import handlers.page as page
import handlers.image as image


# read in the context
from context import context

# add our debug flag to config
context.add('debug', debug)

# set our config into the context
config = context.get('get_config')('scraper')
context.add('config', config)


# configure eventapp to have the # of threads / forks we want
thread_count = config.get('knobs').get('threads_per_stage')
fork_count = config.get('knobs').get('forks')

threaded = config.get('knobs').get('threaded')
multiprocess = config.get('knobs').get('multiprocess')


# set up our event app
app = EventApp('blog_scraper', config, context,

               # HANDLERS

               # catch random page pull requests
               ('timer_scrape_page',
                page.scrape_images,
                'blog_image_found'),

               # find blog images which are good
               (image.filter_bad,
                'blog_image_download_candidate_found'),

               # download good images
               (image.save, 'blog_image_saved'),

               # cell's which have taken damage need to be
               # re-evaluated for scraping
               ('cell_bombed',
                page.investigate_bombed_cells,
                'cell_consumed'),

               # consumed cell = page which needs to be scraped
               (page.scrape_images, 'blog_image_found')
)


# run the app, blocking call
app.run(threaded=threaded, threads=thread_count,
        multiprocess=multiprocess, forks=fork_count)


