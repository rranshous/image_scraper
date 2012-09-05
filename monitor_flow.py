
from eventapp import EventApp

def count_all(event, _int):
    overall_counter = _int('event_type_counter:overal')
    event_counter = _int('event_type_counter:%s' % event.event)

    event_counter.incr()

    if overall_counter % 1000 == 0:
        print
        print '------ REPORT --------'
        for event, count in event_counts.iteritems():
            print '%s: %s' % (event, count)

    overall_counter.incr()

    yield False

app = EventApp('blog_scraper',

               ('.*', count_all, '_'))
app.run()
