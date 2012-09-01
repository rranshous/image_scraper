
from eventapp import EventApp
from hashlib import sha1
import requests
from os.path import join, exists

OUT_DIR = './output/'

proxies = {'http':'http://127.0.0.1:3128',
           'https':'http://127.0.0.1:3128'}

def download(url):
    global proxies
    return requests.get(url, proxies=proxies).content

def handle_found(src_page, src_url):
    image_data = download(src_url)
    sha = sha1(image_data).hexdigest()
    out_path = join(OUT_DIR, sha)
    if not exists(out_path):
        with open(out_path, 'wb') as fh:
            fh.write(image_data)
        print 'writing: %s' % out_path
        yield dict( src_url = src_url,
                    src_page = src_page,
                    download_location='local',
                    download_key=sha )

app = EventApp('image_downloader',

               # we want events about found images
               'image_found',

               handle_found,

               'image_downloaded')

app.run()
