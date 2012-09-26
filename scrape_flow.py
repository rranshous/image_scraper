

from eventapp import EventApp

# we are going to create a flow which scrapes a blog
# and downloads images it hasn't downloaded before

import blog_functions as blog
import page_functions as page
import image_functions as image

# another process has a timer which puts off
# random page process requests

app = EventApp('blog_scraper',

               # catch random page pull requests
               ('timer_scrape_page', page.scrape_images, 'blog_image_found'),

               # find blog images which are good
               (image.filter_bad, 'blog_image_download_candidate_found'),

               # downoad good images
               (image.save, 'blog_image_saved'))

app.run(threaded=False)
