
from inspect import getargspec

# ty rranshous/dss/accessor.py
def get_function_args(func):
    """ returns list of functions args + list of named args """
    arg_spec = getargspec(func)
    return (
        filter(lambda v: v!='self', arg_spec.args or []),
        filter(lambda v: v!='self', arg_spec.keywords or [])
    )

# first handler's args based on incoming events kwarg based args
# any of the initial event's data not handled by initial handler
#   are excluded from further contexts
# lastt handlers yield values should be dicts to map to outgoing event
# all internal state's are done by position sig kwargs
# if handler takes less args than current stack handler is assumed
#   to want newest args (end of stack)
# handlers which return Bools are treated as filterse

from revent import ReventClient

class EventApp(object):
    def __init__(self, name, incoming_event, *args):
        self.name = name
        self.incoming_event = incoming_event
        self.outgoing_event = None
        # if last arg is string, it's outgoing event name
        if isinstance(args[-1], (unicode, basestring)):
            self.outgoing_event = args[-1]
            self.stages = args[:-1]
        else:
            self.stages = args

        # set up a revent connection based on the stages we have
        # each stage is going to emit an event to the next stage which
        # is based on the next stages index in the stage list
        # a 3 stage app will have name_1, name_2 as event names, one and two
        self.rc = ReventClient(self.name, '%s_.+' % self.name, verified=300)
        # we have to have two clients since revent can't support multiple patterns
        # per client right now
        self.incoming_rc = ReventClient(self.name + '_incoming',
                                        self.incoming_event, verified=300)

    def _stage_event_name(self, i):
        return '%s_%s' % (self.name, i)

    def run(self, stopping=None):
        while stopping is None or not stopping.isset():
            self._run()

    def _run(self):
        print 'reading event'

        # look for mid-run events
        event = self.rc.read(block=True, timeout=1)

        # if we didn't find any mid-run events, look for incoming
        if not event:
            event = self.incoming_rc.read(block=True, timeout=1)

        print 'event: %s' % event

        # if we found an event handle it
        if event:
            try:
                self.handle_event(event.event, event.data)
                self.rc.confirm(event)
            except Exception, ex:
                raise
                print 'Exception handling event: %s' % str(ex)
                pass

    def handle_event(self, event_name, event_data):
        """ handles external event coming in """

        # these will be filled out
        stage_index = stage = stage_args = None
        prev_results = []

        print 'handling event: [%s] %s' % (event_name, str(event_data))

        # see if this is the internal or external event
        if event_name.startswith(self.name):

            # it's internal

            # get our stage based on the events name
            stage_index = int(event_name.split('_')[-1])
            stage = self.stages[stage_index]

            # get the stage's args
            args, _ = get_function_args(stage)
            arg_len = len(args)
            prev_results = event_data.get('results')
            # we they want args off the end of the list
            stage_args = prev_results[-arg_len:]

        else:

            # it's exteral
            # we need to map the kwargs in the data to the args
            stage_index = 0
            stage = self.stages[0]
            args, _ = get_function_args(stage)
            stage_args = map(event_data.get, args)
            # the stack of results starts as the one's taken by
            # initial handler
            prev_results = stage_args

        print 'stage:',str(stage)
        print 'stage_index:',str(stage_index)
        print 'stage_args',str(stage_args)

        # all results from the stage become events
        for result in stage(*stage_args):

            print 'stage result:', result

            # internal stages, the next event name will be the next stage
            result_event_name = self._stage_event_name(stage_index + 1)

            # internal events will store their result list under the
            # results key in the event's data
            result_event_data = dict( results = prev_results[:] )

            # if it's a bool than it's a filter. If it's true
            # we re-fire the source event into the next stage
            if result in (True, False):
                if result is False:
                    print 'filtering'
                    continue # don't fire

            # the last stage will put out a dict, this should be fired
            # out as the outgoing event
            elif isinstance(result, dict):
                print 'is last'
                result_event_name = self.outgoing_event
                result_event_data = result

            # just a normal stage, we should update the event's results
            # with this events
            else:
                if isinstance(result, (list,tuple)):
                    result_event_data['results'].extend(result)
                else:
                    result_event_data['results'].append(result)

            assert result_event_name, "missing reuslt event name"
            assert result_event_data, "mssing result event data"
            print 'result event name:', str(result_event_name)
            print 'result event data:', str(result_event_data)
            self.rc.fire(result_event_name, result_event_data)
