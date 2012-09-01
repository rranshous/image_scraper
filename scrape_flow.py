

from eventapp import EventApp

# we are going to create a flow which scrapes a blog
# and downloads images it hasn't downloaded before

from blog_functions import fan_out_blog_pages, filter_seen_pages
from page_functions import scrape_page_for_images, filter_bad_images
from image_functions import get_image_size, save_image, filter_seen_images
from web_functions import get_html, get_data, verify_url

# blog_url, page_url, page_html, image_url, image_size, image_data, image_save_path

app = EventApp('blog_scraper',

               # what event are we taking in
               'timer_scrape_blog',

               # make sure blog exists
               verify_url,

               # fan out the blogs possible pages
               fan_out_blog_pages,

               # check and see if we've hit pages we've
               # seen before
               filter_seen_pages,

               # get the page html
               get_html,

               # scrape the blog page for it's images
               scrape_page_for_images,

               # get the size of the image
               get_image_size,

               # filter the images down to ones which
               # meet our criteria (size, etc)
               filter_bad_images,

               # filter out images we've already seen
               filter_seen_images,

               # download the image
               get_data,

               # save the image down
               save_image)
