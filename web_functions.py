
def get_html(url, config):
    """
    yields HTML or None of url
    """
    try:
        import requests
        proxies = config.get('proxies', {})
        print 'PROXIES: %s' % proxies
        return requests.get(url, proxies=proxies).text
    except:
        raise

def get_data(url, config):
    """
    yields resource data or None
    """
    try:
        import requests
        proxies = config.get('proxies', {})
        print 'PROXIES: %s' % proxies
        return requests.get(url, proxies=proxies).content
    except:
        raise

