

from eventapp import EventApp

# we are going to create a flow which scrapes a blog
# and downloads images it hasn't downloaded before

import blog_functions as blog
import page_functions as page
import image_functions as image

app = EventApp('blog_scraper',

               # make sure blog exists
               ('timer_scrape_blog', blog.verify_url, 'verified_blog_url'),

               # fan out the blogs possible pages
               (blog.fan_out_pages, 'possible_blog_page'),

               # check and see if we've hit pages we've
               # seen before
               (page.filter_seen, 'unseen_blog_page'),

               # scrape the blog page for it's images
               (page.scrape_images, 'blog_image'),

               # get the size of the image
               (image.get_size, 'blog_image_size'),

               # filter the images down to ones which
               # meet our criteria (size, etc)
               (image.filter_bad, 'good_blog_image'),

               # filter out images we've already seen
               (image.filter_seen, 'unseen_blog_image'),

               # save the image down
               (image.save, 'blog_image_saved'))

app.run()
