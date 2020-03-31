import logging
import traceback
from datetime import datetime

import event
from .handler_registry import GetConfig

dateformat = '%Y-%m-%d %H:%M:%S'

def ProcessEvents(g, s):
    config = GetConfig()
    enabled = config.get('enabled', True)
    if enabled is not None and not enabled:
        return

    start_at = config.get('start_at')

    if start_at is None:
        start_at = s.load('start_at')

    if start_at is None:
        start_at = datetime.now()
    else:
        start_at = datetime.strptime(start_at, dateformat)

    newest_event = start_at

    logging.info('Processing events, starting at {}'.format(start_at))
    for e in g.events_since(start_at):
        if e.created_at > newest_event:
            newest_event = e.created_at
            s.store('start_at', newest_event.strftime(dateformat))
        for h in event.Handlers():
            if h.handles(e):
                logging.info('Handling {} with {}'.format(e, h))
                try:
                    h.handle(g, e)
                except Exception as _err:
                    logging.warning('Failure handling {} with {} due to {}: {}'.format(
                            e, h, _err, traceback.format_exc()
                    ))
