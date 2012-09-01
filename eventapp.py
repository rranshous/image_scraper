
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
    def __init__(self, app_name, stage_definitions):

        self.app_name = app_name
        self.stage_definitions = stage_definitions
        self.stages = self._create_stages()

    def run(self):

        # forever
        while True:

            # do one cycle through the stages
            self._run()

    def _run(self):

        # run each stage, having it block for a second so we don't
        # spin our wheels as fast as we can
        for stage in self.stages:
            stage.cycle(block=True, timeout=1)

        return stages

    def _create_stages(self):

        # go through the stage defs, creating a stage for each
        previous_stage = None
        for i, stage_def in enumerate(self.stage_definitions):

            try:
                next_stage = self.stage_definitions[i+1]
            except IndexError:
                next_stage = None

            previous_stage = self._create_stage(stage_def,
                                                previous_stage, next_stage)
            yield previous_stage

    def _create_stage(self, stage_def, previous_stage=None, next_stage=None):

        handler = in_event = out_event = None

        # TODO: update to support multiple handlers per stage def which
        #       would result in multiple stages being created

        # go through each of the pieces in the stage def filling in our reqs
        for arg in stage_def:

            if not handler and callable(arg):
                handler = arg

            elif not in_event:
                in_event = arg

            elif not out_event:
                out_event = arg

        # fill in missing pieces
        if not in_event and previous_stage:
            in_event = previous_stage.out_event

        if not out_event and next_stage:
            out_event = next_stage.in_event

        # make sure we've got everything
        assert handler, "No handler found for stage: " + str(stage_def)
        assert in_event, "No in event found: " + str(stage_def)

        # finally, create our handler
        return AppHandler(self.app_name, in_event, handler, out_event)


class AppHandler(object):

    def __init__(self, app_name, in_event, handler, out_event=None):

        self.app_name
        self.in_event = in_event
        self.handler = handler
        self.handler_args = get_function_args(self.handler)
        self.out_event = out_event

        # sanity checks
        assert in_event, "Must provide in_event"
        assert handler, "Must provide handler"

        # subscribe to our in_event
        channel = '%s-%s' % (app_name, in_event)
        self.rc = ReventClient(channel, in_event, verified=True)

    def cycle(self, block=False, timeout=1):

        # grab up our event
        event = self.rc.read(block=block, timeout=timeout)
        if event:

            # build the handlers input from the event data
            handler_args, handler_kwargs = self._build_handler_args(event)

            # call our handler
            for result in self.handler(*handler_args, *handler_kwargs):

                # see if this results calls for another event to be fired
                result_event = self._build_result_event(event, result)

                # result event is a tuple: (event_name, event_data)
                if result_event:
                    self.rc.fire(*result_event)

    def _build_handler_args(self, event):

        # fill in the args / kwargs from event data
        handler_args = []
        handler_kwargs = {}

        # supports special args such as event, event_name, event_data

        # TODO: better

        for arg in self.handler_args[0]:
            if arg == 'event_data':
                handler_args.append(event.data)
            elif arg == 'event_name':
                handler_args.append(event.name)
            elif arg == 'event':
                handler_args.append(event)
            else:
                handler_args.append(event.data.get(arg))

        for kwarg in self.handler_args[1]:
            if arg == 'event_data':
                handler_kwargs[kwarg] = event.data
            elif arg == 'event_name':
                handler_kwargs[kwarg] = event.name
            elif arg == 'event':
                handler_kwargs[kwarg] = event
            else:
                handler_kwargs[kwarg] = event.data.get(kwarg)

        return handler_args, handler_kwargs

    def _build_result_event(self, event, result):

        # if they didn't define an out event than we aren't putting
        # off events even if we get a result
        if not self.out_event:
            return None

        # if the reuslt is a true or false than it's a filter
        # a false means don't re-fire the event, True means re-fire
        if result is True:
            return event.name, event.data

        # if the reuslt is a dictionary than we're going to use that
        # dict as the resulting event's data
        if isinstance(result, dict):
            return self.out_event, result

        # if it's anything else we're going to update the source event's
        # data to include these results and use resuling data as new
        # events data
        event_data = event.data.copy()
        previous_results = event_data.setdefault('results', [])
        if isinstance(result, (list, tuple)):
            previous_results.extend(result)
        else:
            previous_results.append(result)
        return self.out_event, event_data

