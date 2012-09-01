import requests

proxies = {'http':'127.0.0.1:3128'}

def get_html(url):
    """
    yields HTML or None of url
    """
    try:
        yield requests.get(url, proxies=proxies).html
    except:
        yield None

def get_data(url):
    """
    yields resource data or None
    """
    try:
        yield requests.get(url, proxies=proxies).content
    except:
        yield None

def verify_blog_url(blog_url):
    """
    filter: True if url responds with 200
    """
    try:
        r = requests.get(blog_url, proxies=proxies)
        yield r.status_code == 200
    except Exception, ex:
        yield False
