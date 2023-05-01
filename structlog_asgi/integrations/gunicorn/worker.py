from gunicorn.app.base import BaseApplication


class GunicornStandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        c = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in c.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
