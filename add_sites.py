from revent.lua_client import RedisClient
from hashlib import sha1
import random
import sys

with open('./sites.txt', 'r') as fh:
    urls = [u.strip() for u in fh.readlines() if u.strip()]

rc = RedisClient()
skip_chance = .8
top = 4000
if len(sys.argv) > 1:
    top = int(sys.argv[1])
    print 'top: %s' % top

for i in xrange(0, random.randint(0,top), random.randint(5,20)):

    for url in urls:

        if random.random() < skip_chance:
            continue

        if not url.endswith('/'):
            url+='/'

        print '%s\t%s' % (url, i)

        rc.fire('timer_scrape_page',
                dict(blog_url=url,
                     page_url='%spage/%s' % (url,i),
                     blog_key=sha1(url).hexdigest(),
                     page_number=i))
