from revent.lua_client import RedisClient
from hashlib import sha1

with open('./sites.txt', 'r') as fh:
    urls = [u.strip() for u in fh.readlines() if u.strip()]

rc = RedisClient()

for i in xrange(1, 5000, 100):
    for url in urls:

        if not url.endswith('/'):
            url+='/'

        print '%s\t%s' % (url, i)

        rc.fire('timer_scrape_page',
                dict(blog_url=url,
                     page_url='%spage/%s' % (url,i),
                     blog_key=sha1(url).hexdigest(),
                     page_number=i))
