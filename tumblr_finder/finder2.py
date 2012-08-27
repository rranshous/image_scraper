
from eventapp import EventApp
from blog_scraper import BlogScraper

def handle_blog(blog_url):
    print 'handling blog: %s' % str(blog_url)
    for possible_page_url in BlogScraper._generate_page_urls(blog_url):
        yield possible_page_url

def handle_blog_image(page_url, image_url):
    yield dict( src_page = page_url, src_url = image_url )

def validate_page(url):
    yield BlogScraper.validate_page(url)

# create our event based app
app = EventApp('blog_scraper', # name of app

               # event app will handle
               'timer_scrape_blog',

               # list of handler functions for internal state
               handle_blog,
               validate_page,
               BlogScraper.get_images,
               handle_blog_image,

               # name of event we fire at end of pipe
               'image_found')


app.run()
