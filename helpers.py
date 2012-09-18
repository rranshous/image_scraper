from contextlib import contextmanager
import random as r

@contextmanager
def check_do_work(_signal, blog, page=None, image_url=None,
                  repeat_chance=0.5):
    """
    function which will return bool as to whether we
    should do work for the given piece of data
    """

    # get the signal for this page
    key = '%s:%s:%s' % (blog, page, image_url)
    obj_sig = _signal(key)

    # now get the page's signal's signal
    key = '%s:signal_score:%s' % (key, obj_sig.value)
    obj_sig_score = _signal(key)

    # so now we have a signal which describes the magnitude of
    # the chance of needing to scrape this object, and that signal's
    # score which is the mag chance that the page's signal is correct

    # with these two numbers we must decide if we should do the work
    do_work = False

    # if the signal for the object is better than 0 and
    # the object's signals score is better than 0 i vote we do it
    if obj_sig.value >= 0 and obj_sig_score >= 0:
        do_work = True

    # even if we should do the work, we want to sometimes do it
    # it's the best way to learn!
    if not do_work and r.random() < repeat_chance:
        do_work = True

    # we want a way for the caller to describe whether their
    # work paid off
    def confirm_work(worked):
        if worked:
            obj_sig.incr()
            obj_sig_score.incr()
        else:
            obj_sig.decr()
            obj_sig_score.decr()

    return do_work, confirm_work

def check_do_work(_signal, *objs):

    base_strength = 100
    repeat_chance = 0.05

    # pull the signal for each object as well as the signal's
    # signal.

    key = ''
    signals = []
    for obj in objs:
        key += ':%s' % obj
        obj_signal = _signal(key)
        score_key_bucket = int(obj_signal.value / base_strength)
        score_key = '%s:signal_score:%s' % (key, score_key_bucket)
        obj_signal_score = _signal(score_key)
        signals.append( (obj_signal, obj_signal_score) )


    # calculate a score based on the distance the obj is from the
    # end (and most important) obj's and the obj's score + signal score

    overall_score = 0
    signal_count = len(signals)
    for i, (obj_signal, obj_signal_signal) in enumerate(signals, 1):
        print '%s: %s' % (obj_signal.key, obj_signal.value)
        print '%s: %s' % (obj_signal_signal.key, obj_signal_signal.value)

        # start out w/ the signal's score
        obj_score = obj_signal.value
        # scale by the signals signal's score
        obj_score += obj_signal_signal.value
        # now scale by it's place in the obj list
        obj_score *= i / float(signal_count)

        print 'obj_score: %s' % obj_score
        overall_score += obj_score

    print 'overall_score: %s' % overall_score

    # if the signal is + than we're good ?
    do_work = False

    if overall_score >= 0:
        do_work = True

    # introduce some jiggle
    if not do_work and r.random() < repeat_chance:
        do_work = True

    # we want them to report back to us
    def confirm_work(worked):
        for i, (obj_signal, obj_signal_signal) in enumerate(signals, 1):
            multiplier = i / float(signal_count)
            to_add = int(multiplier * base_strength)
            print 'to_add: %s' % to_add
            if worked:
                obj_signal.incr(to_add)
                obj_signal_signal.incr(to_add)
            else:
                obj_signal.decr(to_add)
                obj_signal_signal.decr(to_add)

    return do_work, confirm_work

@contextmanager
def check_do_work_context(_signal, *objs):
    yield check_do_work(_signal, *objs)
