from contextlib import contextmanager
import random as r

def check_do_work(_signal, *objs):

    base_strength = 100

    # pull the signal for each object as well as the signal's
    # signal.

    key = ''
    signals = []
    for obj in objs:
        key = '%s' % obj
        obj_signal = _signal(key)
        score_key_bucket = int(obj_signal.value / base_strength)
        score_key = '%s:signal_score:%s' % (key, score_key_bucket)
        obj_signal_score = _signal(score_key)
        signals.append( (obj_signal, obj_signal_score) )

    # scale the signals score by the signals signal's
    overall_score = obj_signal.value + obj_signal_score.value

    print 'Score: %s [%s]' % (overall_score, obj_signal.key)

    # if the signal is + than we're good ?
    do_work = False

    if overall_score >= 0:
        do_work = True

    # we want them to report back to us
    def confirm_work(worked):
        signal_count = len(signals)
        for i, (obj_signal, obj_signal_signal) in enumerate(signals, 1):
            multiplier = i / float(signal_count)
            to_add = int(multiplier * base_strength)

            # if it worked than pump up the signal
            if worked:
                obj_signal.incr(to_add)

            # if it didn't work, the signal goes down
            else:
                obj_signal.decr(to_add)

            # if we were right about whether work
            # should be done, pump up the signals signal
            if worked == do_work:
                obj_signal_signal.incr(to_add)

            # if we were wrong .. down we go
            else:
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
