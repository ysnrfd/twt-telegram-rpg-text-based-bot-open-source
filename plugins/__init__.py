class Plugin:
    def __init__(self, bot):
        self.bot = bot
        self._handlers = []

    def _track_handler(self, reg_func, *args, **kwargs):
        def decorator(func):
            # Register with telebot
            reg_func(*args, **kwargs)(func)
            # Keep for tracking purposes
            self._handlers.append((reg_func, args, kwargs, func))
            return func
        return decorator

    def message_handler(self, *args, **kwargs):
        return self._track_handler(self.bot.message_handler, *args, **kwargs)

    def callback_query_handler(self, *args, **kwargs):
        return self._track_handler(self.bot.callback_query_handler, *args, **kwargs)

    def register(self):
        """Override this to register commands and handlers."""
        pass

    def unregister(self):
        """Try to clean up handlers - only possible by filtering telebot internals."""
        try:
            if hasattr(self.bot, '_message_handlers'):
                for reg_func, args, kwargs, func in self._handlers:
                    if reg_func == self.bot.message_handler:
                        self.bot._message_handlers = [h for h in self.bot._message_handlers if h['function'] != func]
                    elif reg_func == self.bot.callback_query_handler:
                        self.bot._callback_query_handlers = [h for h in self.bot._callback_query_handlers if h['function'] != func]
        except Exception as e:
            print(f"⚠️ Error while unregistering plugin handlers: {e}")

        self._handlers.clear()
