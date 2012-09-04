
def run():
    from revent import ReventClient
    rc = ReventClient('scraper_timer')

    with open('./sites.txt','r') as fh:
        for line in fh.readlines():
            line = line.strip()
            print line
            rc.fire('timer_scrape_blog', dict(blog_url=line))

if __name__ == "__main__":
    run()
