from contextlib import contextmanager
import random as r

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

        # start out w/ the signal's score
        obj_score = obj_signal.value
        # add the signals signal's score
        obj_score += obj_signal_signal.value
        # now scale by it's place in the obj list
        obj_score *= i / float(signal_count)
        # increment the overall score
        overall_score += obj_score

    print '[%s] Score: %s' % (obj_signal.key, overall_score)

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
            if worked:
                obj_signal.incr(to_add)
                obj_signal_signal.incr(to_add)
            else:
                obj_signal.decr(to_add)
                obj_signal_signal.decr(to_add)

    return do_work, confirm_work

@contextmanager
def check_do_work_context(_signal, *objs):
    """
    if work is not to be done, dont run the context
    """
    do_work, confirm = check_do_work(_signal, *objs)
    if do_work:
        yield confirm
    else:
        print 'not doing work'
