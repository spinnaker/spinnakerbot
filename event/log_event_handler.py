from .handler import Handler

class LogEventHandler(Handler):
    def __init__(self):
        super().__init__()

    def handles(self, event):
        return True

    def handle(self, g, event):
        self.logging.info('{} ({}): @{} -> {}'.format(event.repo.name, event.created_at, event.actor.login, event.type))
        if self.config.get('payload'):
            self.logging.info('  {}'.format(event.payload))

LogEventHandler()
