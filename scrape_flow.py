from os.path import abspath, dirname, join as path_join
from casconfig import CasConfig
import helpers
import sys
debug = 'debug' in sys.argv
print 'debug: %s' % debug

from eventapp import EventApp
import eventapp

# we are going to create a flow which scrapes a blog
# and downloads images it hasn't downloaded before

import page_functions as page
import image_functions as image
import web_functions as web

# read in our config
here = dirname(abspath(__file__))
config_path = path_join(here, 'config')
config_type = 'production' if not debug else 'development'

print 'reading config [%s]: %s' % (config_type, config_path)

config = CasConfig(config_path)
config.setup(config_type)
print 'config: %s' % config

# another process has a timer which puts off
# random page process requests

# the timer_scrape_page event needs to have:
#   blog_url, blog_key, page_url, page_number

app = EventApp('blog_scraper', config,

               { 'upload_image': helpers.upload_image,
                 'get_html': web.get_html,
                 'get_data': web.get_data,
                 'save_new_image': helpers.upload_image,
                 'get_saved_image': helpers.retrieve_image
               }

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


eventapp.threads_per_stage = config.get('knobs').get('threads_per_stage')
eventapp.forks = config.get('knobs').get('forks')
threaded = config.get('knobs').get('threaded')
multiprocess = config.get('knobs').get('multiprocess')

app.run(threaded=True, multiprocess=False)
