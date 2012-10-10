from os.path import abspath, dirname, join as path_join
import sys

## WSGI app for image-scraper

# what dir is this file in ?
here = dirname(abspath(__file__))

# update our python path to be at root of project
base = dirname(here)
sys.path.insert(0, base)

# we default to production
debug = 'debug' in sys.argv
print 'debug: %s' % debug

# read in our config
from casconfig import CasConfig
config_path = path_join(base, 'config')
config_type = 'production' if not debug else 'development'
print 'reading config [%s]: %s' % (config_type, config_path)
config = CasConfig(config_path)
config.setup(config_type)
print 'config: %s' % config

# OBJECTS
from objects.blog import Blog
from objects.image import Image

# and we def need our context
from lib.eventapp.bubbles import build_context

# and our helpers
import lib.helpers as helpers

# FLASK it up !
from flask import Flask, Response, redirect

# create our app
app = Flask('image-scraper')

# CONTEXT

context = build_context({
    'Image': Image,
    'Blog': Blog,
    'config': config,
    'retrieve_image': helpers.retrieve_image,
    'get_image_public_url': helpers.get_image_public_url
})


# OUR HANDLERS

@app.route("/blogs/")
@context.decorate
def show_blogs(Blog):
    output = ''

    for blog in Blog.collection.find():
        output += """
        <a href="./{short_hash}/">{url}</a>
        <hr/>
        """.format(short_hash=blog.short_hash,
                   url=blog.url)

    return output


@app.route("/blogs/<short_hash>/<int:start>/<int:end>/")
@app.route("/blogs/<short_hash>/<int:start>/")
@app.route("/blogs/<short_hash>/")
@context.decorate
def most_recent(short_hash, Image, start=0, end=50):

    range_len = end - start
    print 'range len: %s' % range_len
    next_first = start + range_len + 1
    print 'next first: %s' % next_first
    next_last = next_first + range_len
    print 'next_last: %s' % next_last

    pagenate = """
    <a href="/blogs/{short_hash}/{next_first}/{next_last}/">
        {next_first} -> {next_last}
    </a>
    <hr/>
    """.format(short_hash = short_hash,
               next_first = next_first,
               next_last = next_last)

    output = ''
    output += pagenate
    images = Image.collection.find({
                'blogs.'+short_hash: {'$exists': True},
                'downloaded':True})
    newest_images = images.skip(next_first)
    newest_images = images.limit(range_len)
    print 'short_hash: %s' % short_hash
    for image in newest_images:
        print 'image: %s' % image
        output += """
        <a href="/images/{short_hash}/data/">
        <img src="/images/{short_hash}/data/">
        </img></a>
        <hr/>
        """.format(short_hash=image.short_hash)
    output += pagenate

    return output


@app.route("/images/<short_hash>/data/")
@context.decorate
def image_data(short_hash, Image, context):

    image = Image.get_one(short_hash=short_hash)
    if not image:
        return 'not found'

    # go directly to the source
    url = context.create_partial(image.get_public_url)()
    return redirect(url)

    # TODO: stream
    fn = context.create_partial(image.get_data)
    data_stream = fn(stream=True)
    return Response(data_stream, mimetype='image')


# start our app from the command line
if __name__ == "__main__":
    app.run(debug=debug, host='0.0.0.0')

