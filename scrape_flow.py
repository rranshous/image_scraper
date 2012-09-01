

from eventapp import EventApp

# we are going to create a flow which scrapes a blog
# and downloads images it hasn't downloaded before

import blog_functions as blog
import page_functions as page
import image_functions as image

# blog_url, page_url, page_html, image_url, image_size, image_data, image_save_path

app = EventApp('blog_scraper',

               # what event are we taking in
               'timer_scrape_blog',

               # make sure blog exists
               blog.verify_url,

               # fan out the blogs possible pages
               blog.fan_out_pages,

               # check and see if we've hit pages we've
               # seen before
               page.filter_seen,

               # get the page html
               page.get_html,

               # scrape the blog page for it's images
               page.scrape_images,

               # get the size of the image
               image.get_size,

               # filter the images down to ones which
               # meet our criteria (size, etc)
               image.filter_bad,

               # filter out images we've already seen
               image.filter_seen,

               # download the image
               image.get_data,

               # save the image down
               image.save,

               # broadcast what we've done
               image.broadcast_save,

               'image_saved')

app.run()
