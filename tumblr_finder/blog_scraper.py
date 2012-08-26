from itertools import ifilter
from operator import itemgetter
from bs4 import BeautifulSoup as BS
import requests

proxies = None
def get_html(url):
    """
    requests the given url and returns the resulting_html
    expects url will return html
    """
    global proxies
    return requests.get(url, proxies=proxies).text

class BlogScraper(object):
    """
    Object which encapsulates logic for downloading
    images from image blogs on tumblr
    """

    def __init__(self, blog_root_url):
        self.root_url = blog_root_url
        if not self.root_url.endswith('/'):
            self.root_url += '/'
        self.min_img_size = 300
        self.max_pages = 1000

    def generate_page_urls(self):
        print 'generating page urls'
        for url in self._generate_page_urls(self.root_url, self.max_pages):
            yield url

    @staticmethod
    def _generate_page_urls(root_url, max_pages=10):
        for i in xrange(1, max_pages):
            yield root_url + 'page/' + str(i)

    @staticmethod
    def validate_page(url):
        """
        validates that the guessed url is page worth looking at

        return True if the URL should be inspected, else False
        """

        # download the url's content
        html = get_html(url)

        try:
            # check for the word post in the html, this is a simple check
            # to make sure it's not an error page
            # TODO: better
            if html and 'post' in html:
                return True

        except Exception, ex:
            print 'exception validating page: %s' % ex

        return False

    @staticmethod
    def get_images(url):
        """
        returns an iterator of image urls which are found
        in the given url
        """
        # get the page's html
        html = get_html(url)

        try:
            # create a soup from it
            soup = BS(html)

        except Exception, ex:
            print 'Exception making soup: %s' % str(ex)
            yield []

        for src in imap(itemgetter('src'), soup.find_all('img')):
            yield src

    def _validate_pic_url(self, url):
        """
        checks whether passed url appears to be to a valid image

        return True if appears valid, else False
        """
        patterns = ['media.tumblr.com','tumblr.com/photo']
        found = False
        for p in patterns:
            if p in src:
                # attempt to get the images size from the url
                size = src[-7:-4]
                if size.isdigit() and int(size) > self.min_img_size:
                    return True
        return False

    def filter_pic_urls(self, urls):
        """
        filters passed urls iterator.

        returns iterator which is filtered set of urls
        which appear to be valid content for downloading
        """

        return ifilter(self._validate_pic_url, urls)


    def get_images(self):
        """
        generator: yields image_url, source_page_url
        """

        for page_url in self.generate_page_urls():
            for image_url in self.get_page_images(page_url):
                yield image_url, page_url

    def get_page_images(self, page_url):
        """
        iterative version of update (see update)
        """

        # make sure it's a valid page, if it's not valid than we've inspected
        # all possible pages, we should return
        if self.validate_page(page_url):

            # get an iterator of all the images on the page
            image_urls = self.get_images(page_url)

            # go through the good img urls, collecting to return
            images = []
            for image_url in self.filter_pic_urls(image_urls):

                # we should find image data
                assert image_data, "image found no data"

                # send up the image we found
                yield image_url
