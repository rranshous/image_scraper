from os.path import abspath, dirname, join as path_join
from casconfig import CasConfig
import helpers
import sys
production = 'production' in sys.argv

from eventapp import EventApp
import eventapp

# we are going to create a flow which scrapes a blog
# and downloads images it hasn't downloaded before

import blog_functions as blog
import page_functions as page
import image_functions as image

# read in our config
here = dirname(abspath(__file__))
config_path = path_join(here, 'config')
config_type = 'production' if production else 'development'
print 'reading config [%s]: %s' % (config_type, config_path)
config = CasConfig(config_path)
config.setup(config_type)
print
print 'config:'
print config
print

exit

# another process has a timer which puts off
# random page process requests

# the timer_scrape_page event needs to have:
#   blog_url, blog_key, page_url, page_number

app = EventApp('blog_scraper', config,
               { 'upload_image': helpers.upload_image },

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


eventapp.threads_per_stage = 2
eventapp.processes_per_stage = 2

app.run(threaded=True, multiprocess=True)
