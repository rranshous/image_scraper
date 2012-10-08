from os.path import abspath, dirname, join as path_join
import sys
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

# our misc helpers
import lib.helpers as helpers

# bring in the event handler functions
import handlers.page as page
import handlers.image as image

# read in our config
from casconfig import CasConfig
config_path = path_join(base, 'config')
config_type = 'production' if not debug else 'development'
print 'reading config [%s]: %s' % (config_type, config_path)
config = CasConfig(config_path)
config.setup(config_type)
print 'config: %s' % config

# import our Mongo backed Image obj
import objects.image

# update our Image object to use the correct DB
mongo_config = config.get('mongodb')
objects.image.Meta.host = mongo_config.get('host')
objects.image.Meta.port = mongo_config.get('port')

# set up our event app
app = EventApp('blog_scraper', config,

               ## base context for handlers
               { 'upload_image': helpers.upload_image,
                 'get_html': helpers.get_html,
                 'get_data': helpers.get_data,
                 'save_new_image': helpers.upload_image,
                 'get_saved_image': helpers.retrieve_image,
                 'bomb': helpers.bomb,
                 'short_hash': helpers.short_hash,
                 'CellDamage': helpers.CellDamage,
                 'generate_page_url': helpers.generate_page_url,
                 'image_size_from_url': helpers.image_size_from_url,
                 'Image': objects.image.Image
               },

               ## handlers

               # catch random page pull requests
               ('timer_scrape_page', page.scrape_images, 'blog_image_found'),

               # find blog images which are good
               (image.filter_bad, 'blog_image_download_candidate_found'),

               # download good images
               (image.save, 'blog_image_saved'),

               # cell's which have taken damage need to be re-evaluated for scraping
               ('cell_bombed', page.investigate_bombed_cells, 'cell_consumed'),

               # consumed cell = page which needs to be scraped
               (page.scrape_images, 'blog_image_found'))

# configure eventapp to have the # of threads / forks we want
eventapp.threads_per_stage = config.get('knobs').get('threads_per_stage')
eventapp.forks = config.get('knobs').get('forks')
threaded = config.get('knobs').get('threaded')
multiprocess = config.get('knobs').get('multiprocess')

# run the app, blocking call
app.run(threaded=threaded, multiprocess=multiprocess)
